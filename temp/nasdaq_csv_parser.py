import csv
import os
import json
import sys
from datetime import datetime
from collections import defaultdict

# CSV 필드 크기 제한 해제
def increase_csv_field_limit():
    """CSV 필드 크기 제한을 늘리는 함수"""
    maxInt = sys.maxsize
    while True:
        try:
            csv.field_size_limit(maxInt)
            break
        except OverflowError:
            maxInt = int(maxInt/10)
    
    print(f"✅ CSV 필드 크기 제한을 {maxInt}로 설정했습니다.")

def parse_nasdaq_csv_by_company(csv_file_path, output_dir):
    """
    NASDAQ CSV 파일을 회사별로 파싱하여 JSON 파일로 저장
    
    Args:
        csv_file_path (str): NASDAQ CSV 파일 경로
        output_dir (str): 출력 디렉토리 경로
    """
    if not os.path.exists(csv_file_path):
        print(f"❌ 파일을 찾을 수 없습니다: {csv_file_path}")
        return
    
    try:
        # CSV 필드 크기 제한 해제
        increase_csv_field_limit()
        
        # 회사별 데이터를 저장할 딕셔너리
        company_data = defaultdict(lambda: defaultdict(list))
        
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            
            print("🔄 NASDAQ CSV 파일을 파싱하고 있습니다...")
            
            for row in csv_reader:
                # Stock_symbol 컬럼에서 회사 심볼 추출
                stock_symbol = row.get('Stock_symbol', '').strip()
                
                if not stock_symbol:
                    continue
                
                # 날짜 정보 처리
                date_str = row.get('Date', '')
                if date_str:
                    try:
                        # 날짜 문자열을 파싱하여 YYYY-MM-DD 형식으로 변환
                        dt = datetime.fromisoformat(date_str.replace(' UTC', ''))
                        date_key = dt.strftime('%Y-%m-%d')
                    except:
                        # 파싱 실패시 원본 사용
                        date_key = date_str.split(' ')[0] if ' ' in date_str else date_str
                else:
                    date_key = 'unknown_date'
                
                # 뉴스 데이터 구성 (원본 데이터 그대로 유지)
                news_item = {
                    "category": "company",
                    "datetime": int(dt.timestamp()) if 'dt' in locals() else 0,
                    "headline": row.get('Article_title', ''),
                    "id": hash(row.get('Url', '')) % 100000000,  # URL을 기반으로 ID 생성
                    "image": "",
                    "related": stock_symbol,
                    "source": row.get('Publisher', 'NASDAQ'),
                    "summary": row.get('Lexrank_summary', ''),  # 원본 그대로 유지
                    "url": row.get('Url', '')
                }
                
                # 회사별로 데이터 저장
                company_data[stock_symbol][date_key].append(news_item)
            
            print(f"✅ 총 {len(company_data)}개 회사의 데이터를 파싱했습니다.")
            
            # 출력 디렉토리 생성
            os.makedirs(output_dir, exist_ok=True)
            
            # 각 회사별로 JSON 파일 생성
            for company_symbol, date_news in company_data.items():
                output_file = os.path.join(output_dir, f"{company_symbol}_data_formatted.json")
                
                # 날짜별로 정렬된 데이터 구성
                sorted_data = {}
                for date, news_list in date_news.items():
                    # 날짜별로 뉴스 정렬 (최신순)
                    sorted_news = sorted(news_list, key=lambda x: x['datetime'], reverse=True)
                    sorted_data[date] = sorted_news
                
                # JSON 파일로 저장
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(sorted_data, f, indent=2, ensure_ascii=False)
                
                total_news = sum(len(news_list) for news_list in date_news.values())
                print(f"📁 {company_symbol}: {len(date_news)}일, {total_news}개 뉴스 → {output_file}")
            
            print(f"\n🎉 모든 회사별 데이터가 {output_dir}에 저장되었습니다!")
            
            # 통계 정보 출력
            print(f"\n📊 통계 정보:")
            print(f"총 회사 수: {len(company_data)}")
            total_news_count = sum(
                sum(len(news_list) for news_list in date_news.values())
                for date_news in company_data.values()
            )
            print(f"총 뉴스 수: {total_news_count}")
            
            # 가장 많은 뉴스가 있는 회사 TOP 5
            company_news_count = {
                symbol: sum(len(news_list) for news_list in date_news.values())
                for symbol, date_news in company_data.items()
            }
            
            print(f"\n 뉴스가 가장 많은 회사 TOP 5:")
            for i, (symbol, count) in enumerate(
                sorted(company_news_count.items(), key=lambda x: x[1], reverse=True)[:5], 1
            ):
                print(f"  {i}. {symbol}: {count}개 뉴스")
                
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

def main():
    """메인 함수"""
    # CSV 파일 경로
    csv_file = "/workspace/data_temp/temp/nasdaq_exteral_data.csv"
    
    # 출력 디렉토리
    output_dir = "/workspace/data_temp/data/finnhub_data/news_data"
    
    print("📊 NASDAQ CSV 회사별 파싱 도구")
    print("=" * 60)
    
    # 회사별 파싱 실행
    parse_nasdaq_csv_by_company(csv_file, output_dir)

if __name__ == "__main__":
    main() 