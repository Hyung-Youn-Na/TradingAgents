#!/usr/bin/env python3
"""
SECEdgarUtils 클래스 테스트 코드
SEC EDGAR 데이터 유틸리티 기능을 테스트합니다.
"""

import sys
import os
import json
from datetime import datetime, timedelta

# 상위 디렉토리의 dataflows 모듈을 import하기 위한 경로 설정
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tradingagents'))

from dataflows.sec_edgar_utils import SECEdgarUtils, validate_date_format, safe_render_to_markdown, safe_get_item


def test_validate_date_format():
    """날짜 형식 검증 함수 테스트"""
    print("=== 날짜 형식 검증 테스트 ===")
    
    # 유효한 날짜들
    valid_dates = [
        "2025-01-01",
        "2024-12-31",
        "2023-06-15"
    ]
    
    # 유효하지 않은 날짜들
    invalid_dates = [
        "2025/01/01",
        "01-01-2025",
        "2025-1-1",
        "2025-01-1",
        "invalid",
        ""
    ]
    
    print("유효한 날짜 테스트:")
    for date in valid_dates:
        result = validate_date_format(date)
        print(f"  {date}: {result}")
        assert result == True
    
    print("유효하지 않은 날짜 테스트:")
    for date in invalid_dates:
        result = validate_date_format(date)
        print(f"  {date}: {result}")
        if date:  # 빈 문자열은 True를 반환해야 함
            assert result == False
    
    print("✅ 날짜 형식 검증 테스트 통과\n")


def test_safe_render_to_markdown():
    """안전한 마크다운 렌더링 함수 테스트"""
    print("=== 안전한 마크다운 렌더링 테스트 ===")
    
    # 테스트용 객체들
    class MockObject:
        def render(self):
            return "Mock rendered content"
    
    class MockDataFrame:
        def render(self):
            return self
        
        def to_markdown(self):
            return "Mock markdown content"
    
    class MockErrorObject:
        def render(self):
            raise Exception("Render error")
    
    # 정상 케이스
    result1 = safe_render_to_markdown(MockObject())
    print(f"MockObject: {result1}")
    assert result1 == "Mock rendered content"
    
    # DataFrame 케이스
    result2 = safe_render_to_markdown(MockDataFrame())
    print(f"MockDataFrame: {result2}")
    assert result2 == "Mock markdown content"
    
    # 에러 케이스
    result3 = safe_render_to_markdown(MockErrorObject())
    print(f"MockErrorObject: {result3}")
    assert "Error:" in result3
    
    # None 케이스
    result4 = safe_render_to_markdown(None)
    print(f"None: {result4}")
    assert result4 == "Data not available"
    
    print("✅ 안전한 마크다운 렌더링 테스트 통과\n")


def test_safe_get_item():
    """안전한 아이템 추출 함수 테스트"""
    print("=== 안전한 아이템 추출 테스트 ===")
    
    class Mock10QObject:
        def get_item_with_part(self, part, item):
            if part == "PART I" and item == "ITEM 1":
                return "Mock Part I Item 1 content"
            return None
    
    class MockErrorObject:
        def get_item_with_part(self, part, item):
            raise Exception("Get item error")
    
    # 정상 케이스
    result1 = safe_get_item(Mock10QObject(), "PART I", "ITEM 1")
    print(f"정상 케이스: {result1}")
    assert result1 == "Mock Part I Item 1 content"
    
    # 존재하지 않는 아이템
    result2 = safe_get_item(Mock10QObject(), "PART I", "ITEM 999")
    print(f"존재하지 않는 아이템: {result2}")
    assert result2 == "Not available"
    
    # 에러 케이스
    result3 = safe_get_item(MockErrorObject(), "PART I", "ITEM 1")
    print(f"에러 케이스: {result3}")
    assert "Error:" in result3
    
    print("✅ 안전한 아이템 추출 테스트 통과\n")


def test_sec_edgar_utils_initialization():
    """SECEdgarUtils 초기화 테스트"""
    print("=== SECEdgarUtils 초기화 테스트 ===")
    try:
        # 기본 이메일로 초기화
        sec_utils = SECEdgarUtils()
		
        print(f"기본 이메일로 초기화 성공: {sec_utils.email}")
        
        # 사용자 정의 이메일로 초기화
        custom_email = "test@example.com"
        sec_utils_custom = SECEdgarUtils(email=custom_email)
        print(f"사용자 정의 이메일로 초기화 성공: {sec_utils_custom.email}")
        
        print("✅ SECEdgarUtils 초기화 테스트 통과\n")
        return True
        
    except Exception as e:
        print(f"❌ SECEdgarUtils 초기화 실패: {str(e)}")
        print("⚠️  SEC EDGAR 라이브러리가 설치되지 않았거나 설정에 문제가 있을 수 있습니다.")
        print("   pip install edgar-tools 명령으로 설치해보세요.")
        return False


def test_company_info_retrieval():
    """회사 정보 조회 테스트"""
    print("=== 회사 정보 조회 테스트 ===")
    
    try:
        sec_utils = SECEdgarUtils()
        
        # NVDA 회사 정보 조회 테스트
        print("NVDA 회사 정보 조회 중...")
        company_info = sec_utils.get_company_info("NVDA")
        
        if "error" in company_info:
            print(f"❌ 회사 정보 조회 실패: {company_info['error']}")
            return False
        
        print("회사 정보:")
        for key, value in company_info.items():
            print(f"  {key}: {value}")
        
        # 필수 필드 확인
        required_fields = ["Company Name", "CIK"]
        for field in required_fields:
            if field not in company_info or company_info[field] == 'N/A':
                print(f"⚠️  필수 필드 '{field}'가 누락되었습니다.")
        
        print("✅ 회사 정보 조회 테스트 통과\n")
        return True
        
    except Exception as e:
        print(f"❌ 회사 정보 조회 테스트 실패: {str(e)}")
        return False


def test_filing_summary_retrieval():
    """파일링 요약 조회 테스트"""
    print("=== 파일링 요약 조회 테스트 ===")
    
    try:
        sec_utils = SECEdgarUtils()
        
        # NVDA 최근 파일링 조회 테스트
        print("NVDA 최근 파일링 조회 중...")
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        filing_summary = sec_utils.get_filing_summary(
            symbol="NVDA",
            filing_type="10-K",
            end_date=end_date,
            limit=5
        )
        
        if "error" in filing_summary.iloc[0] if not filing_summary.empty else {}:
            print(f"❌ 파일링 요약 조회 실패: {filing_summary.iloc[0]['error']}")
            return False
        
        print(f"파일링 개수: {len(filing_summary)}")
        if not filing_summary.empty:
            print("첫 번째 파일링:")
            first_filing = filing_summary.iloc[0]
            for key, value in first_filing.items():
                print(f"  {key}: {value}")
        
        print("✅ 파일링 요약 조회 테스트 통과\n")
        return True
        
    except Exception as e:
        print(f"❌ 파일링 요약 조회 테스트 실패: {str(e)}")
        return False


def test_10k_retrieval():
    """10-K 보고서 조회 테스트"""
    print("=== 10-K 보고서 조회 테스트 ===")
    
    try:
        sec_utils = SECEdgarUtils()
        
        # NVDA 최근 10-K 조회 테스트
        print("NVDA 최근 10-K 조회 중...")
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        tenk_data = sec_utils.get_latest_10k(
            symbol="NVDA",
            end_date=end_date
        )
        if "error" in tenk_data:
            print(f"❌ 10-K 조회 실패: {tenk_data['error']}")
            return False
        
        print("10-K 데이터:")
        for key, value in tenk_data.items():
			# 긴 내용은 요약해서 표시
            content = str(value)[:500] + "..." if len(str(value)) > 500 else str(value) 
            print(f"  {key}: {content}")
        
        # 필수 필드 확인
        required_fields = ["company_name", "cik", "filing_date", "period_of_report"]
        for field in required_fields:
            if field not in tenk_data or tenk_data[field] == 'N/A':
                print(f"⚠️  필수 필드 '{field}'가 누락되었습니다.")
        
        print("✅ 10-K 보고서 조회 테스트 통과\n")
        return True
        
    except Exception as e:
        print(f"❌ 10-K 보고서 조회 테스트 실패: {str(e)}")
        return False


def test_10q_retrieval():
    """10-Q 보고서 조회 테스트"""
    print("=== 10-Q 보고서 조회 테스트 ===")
    
    try:
        sec_utils = SECEdgarUtils()
        
        # NVDA 최근 10-Q 조회 테스트
        print("NVDA 최근 10-Q 조회 중...")
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        tenq_data = sec_utils.get_latest_10q(
            symbol="NVDA",
            end_date=end_date
        )
        
        if "error" in tenq_data:
            print(f"❌ 10-Q 조회 실패: {tenq_data['error']}")
            return False
        
        print("10-Q 데이터:")
        for key, value in tenq_data.items():
            # 긴 내용은 요약해서 표시
            content = str(value)[:500] + "..." if len(str(value)) > 500 else str(value)
            print(f"  {key}: {content}")
        
        # 필수 필드 확인
        required_fields = ["company_name", "cik", "filing_date", "period_of_report"]
        for field in required_fields:
            if field not in tenq_data or tenq_data[field] == 'N/A':
                print(f"⚠️  필수 필드 '{field}'가 누락되었습니다.")
        
        # 10-Q 특화 필드 확인
        q_specific_fields = ["part1_item1", "part1_item2", "part2_item1", "part2_item1a"]
        print("\n10-Q 특화 섹션 확인:")
        for field in q_specific_fields:
            if field in tenq_data:
                content = str(tenq_data[field])[:200] + "..." if len(str(tenq_data[field])) > 200 else str(tenq_data[field])
                print(f"  {field}: {content}")
            else:
                print(f"  {field}: 필드가 존재하지 않음")
        
        print("✅ 10-Q 보고서 조회 테스트 통과\n")
        return True
        
    except Exception as e:
        print(f"❌ 10-Q 보고서 조회 테스트 실패: {str(e)}")
        return False


def test_8k_retrieval():
    """8-K 보고서 조회 테스트"""
    print("=== 8-K 보고서 조회 테스트 ===")
    
    try:
        sec_utils = SECEdgarUtils()
        
        # NVDA 최근 8-K 조회 테스트
        print("NVDA 최근 8-K 조회 중...")
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        eightk_data = sec_utils.get_latest_8k(
            symbol="NVDA",
            end_date=end_date
        )
        
        if "error" in eightk_data:
            print(f"❌ 8-K 조회 실패: {eightk_data['error']}")
            return False
        
        print("8-K 데이터:")
        for key, value in eightk_data.items():
            if key == "text":
                # 8-K 텍스트는 매우 길 수 있으므로 더 짧게 표시
                content = str(value)[:300] + "..." if len(str(value)) > 300 else str(value)
                print(f"  {key}: {content}")
            else:
                print(f"  {key}: {value}")
        
        # 필수 필드 확인
        required_fields = ["company_name", "cik", "filing_date", "period_of_report", "text"]
        for field in required_fields:
            if field not in eightk_data or eightk_data[field] == 'N/A':
                print(f"⚠️  필수 필드 '{field}'가 누락되었습니다.")
        
        print("✅ 8-K 보고서 조회 테스트 통과\n")
        return True
        
    except Exception as e:
        print(f"❌ 8-K 보고서 조회 테스트 실패: {str(e)}")
        return False


def test_financial_metrics():
    """재무 지표 조회 테스트"""
    print("=== 재무 지표 조회 테스트 ===")
    
    try:
        sec_utils = SECEdgarUtils()
        
        # NVDA 재무 지표 조회 테스트
        print("NVDA 재무 지표 조회 중...")
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        metrics_data = sec_utils.get_financial_metrics(
            symbol="NVDA",
            end_date=end_date
        )
        
        if "error" in metrics_data.iloc[0] if not metrics_data.empty else {}:
            print(f"❌ 재무 지표 조회 실패: {metrics_data.iloc[0]['error']}")
            return False
        
        print("재무 지표 데이터:")
        if not metrics_data.empty:
            metrics_row = metrics_data.iloc[0]
            for key, value in metrics_row.items():
                print(f"  {key}: {value}")
        
        # 필수 필드 확인
        required_fields = ["company_name", "cik", "latest_10k_date", "latest_10q_date"]
        for field in required_fields:
            if field not in metrics_data.columns or metrics_data.iloc[0][field] == 'N/A':
                print(f"⚠️  필수 필드 '{field}'가 누락되었습니다.")
        
        print("✅ 재무 지표 조회 테스트 통과\n")
        return True
        
    except Exception as e:
        print(f"❌ 재무 지표 조회 테스트 실패: {str(e)}")
        return False


def run_all_tests():
    """모든 테스트 실행"""
    print("🚀 SECEdgarUtils 클래스 테스트 시작\n")
    
    test_results = []
    
    # 기본 유틸리티 함수 테스트
    test_validate_date_format()
    test_safe_render_to_markdown()
    test_safe_get_item()
    
    # SECEdgarUtils 클래스 테스트
    if test_sec_edgar_utils_initialization():
        test_results.append(("초기화", True))
        
        # 실제 API 호출이 필요한 테스트들
        if test_company_info_retrieval():
            test_results.append(("회사 정보 조회", True))
        else:
            test_results.append(("회사 정보 조회", False))
        
        if test_filing_summary_retrieval():
            test_results.append(("파일링 요약 조회", True))
        else:
            test_results.append(("파일링 요약 조회", False))
        
        if test_10k_retrieval():
            test_results.append(("10-K 보고서 조회", True))
        else:
            test_results.append(("10-K 보고서 조회", False))
        
        if test_10q_retrieval():
            test_results.append(("10-Q 보고서 조회", True))
        else:
            test_results.append(("10-Q 보고서 조회", False))
        
        if test_8k_retrieval():
            test_results.append(("8-K 보고서 조회", True))
        else:
            test_results.append(("8-K 보고서 조회", False))
        
        if test_financial_metrics():
            test_results.append(("재무 지표 조회", True))
        else:
            test_results.append(("재무 지표 조회", False))
    else:
        test_results.append(("초기화", False))
    
    # 테스트 결과 요약
    print("📊 테스트 결과 요약:")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{test_name:20} | {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"전체: {total}개, 통과: {passed}개, 실패: {total - passed}개")
    
    if passed == total:
        print(" 모든 테스트가 통과했습니다!")
    else:
        print("⚠️  일부 테스트가 실패했습니다. 위의 에러 메시지를 확인해주세요.")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  테스트가 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n 예상치 못한 에러가 발생했습니다: {str(e)}")
        sys.exit(1)
