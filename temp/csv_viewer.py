import csv
import os
import json
import sys
from datetime import datetime
from collections import Counter

# CSV 필드 크기 제한 해제
def increase_csv_field_limit():
    """CSV 필드 크기 제한을 늘리는 함수"""
    # 기본 제한 확인
    maxInt = sys.maxsize
    while True:
        try:
            csv.field_size_limit(maxInt)
            break
        except OverflowError:
            maxInt = int(maxInt/10)
    
    print(f"✅ CSV 필드 크기 제한을 {maxInt}로 설정했습니다.")

def view_csv_info(csv_file_path):
    """
    CSV 파일의 기본 정보를 확인하는 함수
    
    Args:
        csv_file_path (str): CSV 파일 경로
    """
    if not os.path.exists(csv_file_path):
        print(f"❌ 파일을 찾을 수 없습니다: {csv_file_path}")
        return
    
    try:
        # CSV 필드 크기 제한 해제
        increase_csv_field_limit()
        
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            # CSV 리더 생성
            csv_reader = csv.DictReader(csvfile)
            
            # 모든 행을 읽어서 리스트로 저장
            rows = list(csv_reader)
            
            if not rows:
                print("❌ CSV 파일이 비어있습니다.")
                return
            
            # 기본 정보 출력
            print("=" * 60)
            print("📊 CSV 파일 정보")
            print("=" * 60)
            print(f"📁 파일 경로: {csv_file_path}")
            print(f"📏 파일 크기: {os.path.getsize(csv_file_path) / 1024:.2f} KB")
            print(f" 총 레코드 수: {len(rows)}")
            print(f"️ 컬럼 수: {len(rows[0])}")
            
            # 컬럼 정보 출력
            print(f"\n📋 컬럼 목록:")
            for i, column in enumerate(rows[0].keys(), 1):
                print(f"  {i:2d}. {column}")
            
            # 각 컬럼의 샘플 데이터 출력
            print(f"\n📋 샘플 데이터 (처음 3개 레코드):")
            for i, row in enumerate(rows[:3], 1):
                print(f"\n--- 레코드 {i} ---")
                for key, value in row.items():
                    # 긴 텍스트는 잘라서 표시
                    if len(str(value)) > 100:
                        display_value = str(value)[:100] + "..."
                    else:
                        display_value = str(value)
                    print(f"  {key}: {display_value}")
            
            # datetime 필드가 있다면 날짜 분포 확인
            if 'datetime' in rows[0]:
                print(f"\n📅 날짜 분포:")
                date_counter = Counter()
                for row in rows:
                    try:
                        timestamp = int(row['datetime'])
                        dt = datetime.fromtimestamp(timestamp)
                        date_str = dt.strftime('%Y-%m-%d')
                        date_counter[date_str] += 1
                    except (ValueError, TypeError):
                        continue
                
                # 날짜별 개수 출력 (상위 10개)
                for date, count in date_counter.most_common(10):
                    print(f"  {date}: {count}개")
            
            # source 필드가 있다면 소스 분포 확인
            if 'source' in rows[0]:
                print(f"\n📰 소스 분포:")
                source_counter = Counter()
                for row in rows:
                    source = row.get('source', 'Unknown')
                    if source:
                        source_counter[source] += 1
                
                # 소스별 개수 출력
                for source, count in source_counter.most_common():
                    print(f"  {source}: {count}개")
            
            # category 필드가 있다면 카테고리 분포 확인
            if 'category' in rows[0]:
                print(f"\n🏷️ 카테고리 분포:")
                category_counter = Counter()
                for row in rows:
                    category = row.get('category', 'Unknown')
                    if category:
                        category_counter[category] += 1
                
                # 카테고리별 개수 출력
                for category, count in category_counter.most_common():
                    print(f"  {category}: {count}개")
            
            print("\n" + "=" * 60)
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

def view_csv_sample(csv_file_path, num_samples=5):
    """
    CSV 파일의 샘플 데이터를 보기 좋게 출력하는 함수
    
    Args:
        csv_file_path (str): CSV 파일 경로
        num_samples (int): 출력할 샘플 개수
    """
    if not os.path.exists(csv_file_path):
        print(f"❌ 파일을 찾을 수 없습니다: {csv_file_path}")
        return
    
    try:
        # CSV 필드 크기 제한 해제
        increase_csv_field_limit()
        
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            rows = list(csv_reader)
            
            if not rows:
                print("❌ CSV 파일이 비어있습니다.")
                return
            
            print(f"\n📋 샘플 데이터 ({num_samples}개):")
            print("=" * 80)
            
            for i, row in enumerate(rows[:num_samples], 1):
                print(f"\n🔍 샘플 {i}:")
                print("-" * 40)
                
                for key, value in row.items():
                    # 긴 텍스트는 잘라서 표시
                    if len(str(value)) > 150:
                        display_value = str(value)[:150] + "..."
                    else:
                        display_value = str(value)
                    
                    # datetime 필드 특별 처리
                    if key == 'datetime' and value:
                        try:
                            timestamp = int(value)
                            dt = datetime.fromtimestamp(timestamp)
                            readable_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                            print(f"  {key}: {readable_time} (원본: {value})")
                        except (ValueError, TypeError):
                            print(f"  {key}: {display_value}")
                    else:
                        print(f"  {key}: {display_value}")
            
            print("\n" + "=" * 80)
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

def main():
    """메인 함수"""
    # CSV 파일 경로
    csv_file = "/workspace/data_temp/temp/nasdaq_exteral_data.csv"
    
    print(" CSV 파일 확인 도구")
    print("=" * 60)
    
    # 1. 기본 정보 확인
    view_csv_info(csv_file)
    
    # 2. 샘플 데이터 확인
    view_csv_sample(csv_file, num_samples=3)
    
    # 3. 추가 옵션
    print("\n 추가 옵션:")
    print("1. 더 많은 샘플 보기 (5개)")
    print("2. 특정 날짜의 뉴스만 보기")
    print("3. 특정 소스의 뉴스만 보기")
    print("4. JSON으로 변환")
    
    choice = input("\n선택하세요 (1-4, 엔터로 종료): ").strip()
    
    if choice == "1":
        view_csv_sample(csv_file, num_samples=5)
    elif choice == "2":
        date_filter = input("날짜를 입력하세요 (YYYY-MM-DD): ").strip()
        filter_by_date(csv_file, date_filter)
    elif choice == "3":
        source_filter = input("소스를 입력하세요: ").strip()
        filter_by_source(csv_file, source_filter)
    elif choice == "4":
        print("🔄 JSON 변환을 시작합니다...")
        os.system(f"python temp/csv_to_json_converter.py")

def filter_by_date(csv_file_path, target_date):
    """특정 날짜의 뉴스만 필터링"""
    try:
        # CSV 필드 크기 제한 해제
        increase_csv_field_limit()
        
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            filtered_rows = []
            
            for row in csv_reader:
                try:
                    timestamp = int(row['datetime'])
                    dt = datetime.fromtimestamp(timestamp)
                    row_date = dt.strftime('%Y-%m-%d')
                    
                    if row_date == target_date:
                        filtered_rows.append(row)
                except (ValueError, TypeError):
                    continue
            
            print(f"\n📅 {target_date} 날짜의 뉴스 ({len(filtered_rows)}개):")
            for i, row in enumerate(filtered_rows, 1):
                print(f"\n{i}. {row['headline']}")
                print(f"   소스: {row['source']}")
                print(f"   시간: {datetime.fromtimestamp(int(row['datetime'])).strftime('%H:%M')}")
                
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

def filter_by_source(csv_file_path, target_source):
    """특정 소스의 뉴스만 필터링"""
    try:
        # CSV 필드 크기 제한 해제
        increase_csv_field_limit()
        
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            filtered_rows = []
            
            for row in csv_reader:
                if row.get('source', '').lower() == target_source.lower():
                    filtered_rows.append(row)
            
            print(f"\n {target_source} 소스의 뉴스 ({len(filtered_rows)}개):")
            for i, row in enumerate(filtered_rows[:10], 1):  # 최대 10개만 표시
                print(f"\n{i}. {row['headline']}")
                print(f"   날짜: {datetime.fromtimestamp(int(row['datetime'])).strftime('%Y-%m-%d %H:%M')}")
                
            if len(filtered_rows) > 10:
                print(f"\n... 그리고 {len(filtered_rows) - 10}개 더")
                
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

if __name__ == "__main__":
    main() 