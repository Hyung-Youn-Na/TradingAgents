import csv
import json
import os
from datetime import datetime
from collections import defaultdict

def csv_to_json_grouped_by_date(csv_file_path, json_file_path=None):
    """
    CSV 파일을 날짜별로 그룹화하여 JSON으로 변환하는 함수
    
    Args:
        csv_file_path (str): 입력 CSV 파일 경로
        json_file_path (str): 출력 JSON 파일 경로 (None이면 자동 생성)
    """
    
    # JSON 파일 경로가 지정되지 않으면 자동 생성
    if json_file_path is None:
        base_name = os.path.splitext(os.path.basename(csv_file_path))[0]
        json_file_path = os.path.join(os.path.dirname(csv_file_path), f"{base_name}_grouped.json")
    
    # 날짜별로 그룹화할 딕셔너리
    grouped_data = defaultdict(list)
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            # CSV 리더 생성
            csv_reader = csv.DictReader(csvfile)
            
            # 각 행을 처리
            for row in csv_reader:
                # datetime 필드 처리
                if 'datetime' in row and row['datetime']:
                    try:
                        # Unix timestamp를 datetime 객체로 변환
                        timestamp = int(row['datetime'])
                        dt = datetime.fromtimestamp(timestamp)
                        
                        # 날짜를 YYYY-MM-DD 형식으로 변환
                        date_key = dt.strftime('%Y-%m-%d')
                        
                        # 원본 데이터에서 불필요한 필드 제거하고 필요한 필드만 유지
                        news_item = {
                            "category": row.get('category', ''),
                            "datetime": timestamp,  # 원본 timestamp 유지
                            "headline": row.get('headline', ''),
                            "id": int(row.get('id', 0)) if row.get('id') else 0,
                            "image": row.get('image', ''),
                            "related": row.get('related', ''),
                            "source": row.get('source', ''),
                            "summary": row.get('summary', ''),
                            "url": row.get('url', '')
                        }
                        
                        # 해당 날짜의 리스트에 추가
                        grouped_data[date_key].append(news_item)
                        
                    except (ValueError, TypeError) as e:
                        print(f"⚠️ datetime 변환 오류: {row['datetime']} - {e}")
                        # 변환 실패 시 기본 날짜 사용
                        date_key = "unknown_date"
                        news_item = {
                            "category": row.get('category', ''),
                            "datetime": row.get('datetime', ''),
                            "headline": row.get('headline', ''),
                            "id": int(row.get('id', 0)) if row.get('id') else 0,
                            "image": row.get('image', ''),
                            "related": row.get('related', ''),
                            "source": row.get('source', ''),
                            "summary": row.get('summary', ''),
                            "url": row.get('url', '')
                        }
                        grouped_data[date_key].append(news_item)
        
        # 날짜별로 정렬 (최신 날짜가 먼저 오도록)
        sorted_data = dict(sorted(grouped_data.items(), reverse=True))
        
        # JSON 파일로 저장
        with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(sorted_data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"✅ 변환 완료!")
        print(f"📁 입력 파일: {csv_file_path}")
        print(f"📁 출력 파일: {json_file_path}")
        print(f" 총 {len(sorted_data)}개의 날짜 그룹이 생성되었습니다.")
        
        # 각 날짜별 뉴스 개수 출력
        total_news = sum(len(news_list) for news_list in sorted_data.values())
        print(f" 총 {total_news}개의 뉴스가 변환되었습니다.")
        
        return json_file_path
        
    except FileNotFoundError:
        print(f"❌ 오류: 파일을 찾을 수 없습니다 - {csv_file_path}")
        return None
    except Exception as e:
        print(f"❌ 오류: {str(e)}")
        return None

def csv_to_json_simple(csv_file_path, json_file_path=None):
    """
    CSV 파일을 단순 JSON 배열로 변환하는 함수 (기존 방식)
    
    Args:
        csv_file_path (str): 입력 CSV 파일 경로
        json_file_path (str): 출력 JSON 파일 경로 (None이면 자동 생성)
    """
    
    # JSON 파일 경로가 지정되지 않으면 자동 생성
    if json_file_path is None:
        base_name = os.path.splitext(os.path.basename(csv_file_path))[0]
        json_file_path = os.path.join(os.path.dirname(csv_file_path), f"{base_name}_simple.json")
    
    data = []
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            # CSV 리더 생성
            csv_reader = csv.DictReader(csvfile)
            
            # 각 행을 딕셔너리로 변환하여 리스트에 추가
            for row in csv_reader:
                # datetime 필드를 읽기 쉬운 형태로 변환
                if 'datetime' in row and row['datetime']:
                    try:
                        # Unix timestamp를 datetime 객체로 변환
                        timestamp = int(row['datetime'])
                        dt = datetime.fromtimestamp(timestamp)
                        
                        # 원본 timestamp 유지하면서 읽기 쉬운 형태 추가
                        row['datetime_readable'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                        row['datetime_iso'] = dt.isoformat()
                        row['date'] = dt.strftime('%Y-%m-%d')
                        row['time'] = dt.strftime('%H:%M:%S')
                        row['year'] = dt.year
                        row['month'] = dt.month
                        row['day'] = dt.day
                        row['hour'] = dt.hour
                        row['minute'] = dt.minute
                        row['weekday'] = dt.strftime('%A')  # 요일 이름
                        row['weekday_short'] = dt.strftime('%a')  # 요일 약어
                        
                    except (ValueError, TypeError) as e:
                        print(f"⚠️ datetime 변환 오류: {row['datetime']} - {e}")
                        # 변환 실패 시 원본 값 유지
                        row['datetime_readable'] = row['datetime']
                
                data.append(row)
        
        # JSON 파일로 저장
        with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"✅ 단순 변환 완료!")
        print(f"📁 입력 파일: {csv_file_path}")
        print(f"📁 출력 파일: {json_file_path}")
        print(f" 총 {len(data)}개의 레코드가 변환되었습니다.")
        
        return json_file_path
        
    except FileNotFoundError:
        print(f"❌ 오류: 파일을 찾을 수 없습니다 - {csv_file_path}")
        return None
    except Exception as e:
        print(f"❌ 오류: {str(e)}")
        return None

def main():
    """메인 함수"""
    # CSV 파일 경로
    csv_file = "temp/csv/Google_Daily_News.csv"
    
    print("🔄 CSV를 JSON으로 변환 중...")
    print(f"📂 입력: {csv_file}")
    print("-" * 50)
    
    # 1. 날짜별 그룹화 변환 (참조 포맷과 동일)
    grouped_json_file = "temp/Google_Daily_News_grouped.json"
    print("\n📅 날짜별 그룹화 변환 시작...")
    result1 = csv_to_json_grouped_by_date(csv_file, grouped_json_file)
    
    # 2. 단순 배열 변환 (기존 방식)
    simple_json_file = "temp/Google_Daily_News_simple.json"
    print("\n📋 단순 배열 변환 시작...")
    result2 = csv_to_json_simple(csv_file, simple_json_file)
    
    if result1 and result2:
        print("\n🎉 모든 변환이 성공적으로 완료되었습니다!")
        
        # 파일 크기 정보 출력
        csv_size = os.path.getsize(csv_file) / 1024  # KB
        grouped_size = os.path.getsize(grouped_json_file) / 1024  # KB
        simple_size = os.path.getsize(simple_json_file) / 1024  # KB
        
        print(f"\n📊 파일 크기:")
        print(f"   CSV: {csv_size:.2f} KB")
        print(f"   Grouped JSON: {grouped_size:.2f} KB")
        print(f"   Simple JSON: {simple_size:.2f} KB")
        
        # 그룹화된 데이터의 샘플 출력
        print(f"\n📋 그룹화된 데이터 샘플:")
        with open(grouped_json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            dates = list(data.keys())[:3]  # 처음 3개 날짜
            for date in dates:
                news_list = data[date]
                print(f"\n📅 {date} ({len(news_list)}개 뉴스):")
                for i, news in enumerate(news_list[:2]):  # 각 날짜당 처음 2개 뉴스
                    print(f"  {i+1}. {news['headline'][:80]}...")
                    print(f"     Source: {news['source']}, Time: {datetime.fromtimestamp(news['datetime']).strftime('%H:%M')}")
    else:
        print("❌ 변환에 실패했습니다.")

if __name__ == "__main__":
    main() 