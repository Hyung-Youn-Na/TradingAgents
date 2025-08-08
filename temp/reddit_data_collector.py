import praw
import json
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Optional
import time
from tqdm import tqdm

class RedditDataCollector:
    """
    Reddit API를 사용하여 데이터를 수집하고 프로젝트 구조에 맞게 저장하는 클래스
    """
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str, data_dir: str = "/mnt/trading_agents/reddit"):
        """
        Args:
            client_id (str): Reddit API 클라이언트 ID
            client_secret (str): Reddit API 클라이언트 시크릿
            user_agent (str): Reddit API 사용자 에이전트
            data_dir (str): 데이터 저장 디렉토리
        """
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.data_dir = data_dir
        self.reddit_data_dir = os.path.join(data_dir, "reddit_data")
        
        # 카테고리별 서브레딧 정의
        self.categories = {
            "global_news": [
                "worldnews",
                "news", 
                "politics",
                "economics",
                "business",
                "technology",
                "science"
            ],
            "company_news": [
                "stocks",
                "investing",
                "wallstreetbets",
                "stockmarket",
                "finance",
                "trading",
                "options"
            ]
        }
        
        # 회사명 매핑 (reddit_utils.py와 동일)
        self.ticker_to_company = {
            "AAPL": "Apple",
            # "MSFT": "Microsoft", 
            # "GOOGL": "Google",
            # "AMZN": "Amazon",
            # "TSLA": "Tesla",
            # "NVDA": "Nvidia",
            # "TSM": "Taiwan Semiconductor Manufacturing Company OR TSMC",
            # "JPM": "JPMorgan Chase OR JP Morgan",
            # "JNJ": "Johnson & Johnson OR JNJ",
            # "V": "Visa",
            # "WMT": "Walmart",
            # "META": "Meta OR Facebook",
            # "AMD": "AMD",
            # "INTC": "Intel",
            # "QCOM": "Qualcomm",
            # "BABA": "Alibaba",
            # "ADBE": "Adobe",
            # "NFLX": "Netflix",
            # "CRM": "Salesforce",
            # "PYPL": "PayPal",
            # "PLTR": "Palantir",
            # "MU": "Micron",
            # "SQ": "Block OR Square",
            # "ZM": "Zoom",
            # "CSCO": "Cisco",
            # "SHOP": "Shopify",
            # "ORCL": "Oracle",
            # "X": "Twitter OR X",
            # "SPOT": "Spotify",
            # "AVGO": "Broadcom",
            # "ASML": "ASML",
            # "TWLO": "Twilio",
            # "SNAP": "Snap Inc.",
            # "TEAM": "Atlassian",
            # "SQSP": "Squarespace",
            # "UBER": "Uber",
            # "ROKU": "Roku",
            # "PINS": "Pinterest",
        }
        
        self._create_directories()
    
    def _create_directories(self):
        """필요한 디렉토리들을 생성합니다."""
        for category in self.categories.keys():
            category_dir = os.path.join(self.reddit_data_dir, category)
            os.makedirs(category_dir, exist_ok=True)
            print(f"Created directory: {category_dir}")
    
    def _get_company_search_terms(self, ticker: str) -> List[str]:
        """티커에 해당하는 회사명 검색어들을 반환합니다."""
        if ticker not in self.ticker_to_company:
            return [ticker]
        
        company_name = self.ticker_to_company[ticker]
        if "OR" in company_name:
            search_terms = company_name.split(" OR ")
        else:
            search_terms = [company_name]
        
        # 티커도 검색어에 추가
        search_terms.append(ticker)
        return search_terms
    
    def _is_company_related(self, post, ticker: str) -> bool:
        """포스트가 특정 회사와 관련이 있는지 확인합니다."""
        search_terms = self._get_company_search_terms(ticker)
        
        title = post.title.lower()
        content = post.selftext.lower()
        
        # 더 유연한 검색: 부분 문자열 매칭 추가
        for term in search_terms:
            term_lower = term.lower()
            if (term_lower in title or term_lower in content or
                any(word in title or word in content for word in term_lower.split())):
                return True
        
        return False
    
    def _post_to_dict(self, post) -> Dict:
        """Reddit 포스트를 딕셔너리로 변환합니다."""
        return {
            "created_utc": post.created_utc,
            "id": post.id,
            "title": post.title,
            "selftext": post.selftext,
            "url": post.url,
            "ups": post.ups,
            "downs": getattr(post, 'downs', 0),
            "score": post.score,
            "num_comments": post.num_comments,
            "subreddit": post.subreddit.display_name,
            "author": str(post.author) if post.author else "[deleted]",
            "permalink": f"https://reddit.com{post.permalink}"
        }
    
    def collect_global_news(self, start_date: str, end_date: str, limit_per_subreddit: int = 1000):
        """
        글로벌 뉴스 데이터를 수집합니다.
        
        Args:
            start_date (str): 시작 날짜 (YYYY-MM-DD)
            end_date (str): 종료 날짜 (YYYY-MM-DD)
            limit_per_subreddit (int): 서브레딧당 수집할 포스트 수
        """
        print(f"Collecting global news from {start_date} to {end_date}")
        
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        for subreddit_name in self.categories["global_news"]:
            print(f"Processing subreddit: r/{subreddit_name}")
            
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # JSONL 파일 경로
                jsonl_file_path = os.path.join(
                    self.reddit_data_dir, 
                    "global_news", 
                    f"{subreddit_name}.jsonl"
                )
                
                posts_collected = []
                
                # new 정렬로 변경하여 최신 포스트부터 수집
                for post in subreddit.new(limit=limit_per_subreddit):
                    post_date = datetime.fromtimestamp(post.created_utc)
                    
                    # 날짜 범위 확인
                    if start_dt <= post_date <= end_dt:
                        post_dict = self._post_to_dict(post)
                        posts_collected.append(post_dict)
                
                # JSONL 파일에 저장
                with open(jsonl_file_path, 'w', encoding='utf-8') as f:
                    for post_dict in posts_collected:
                        f.write(json.dumps(post_dict, ensure_ascii=False) + '\n')
                
                print(f"Collected {len(posts_collected)} posts from r/{subreddit_name}")
                
                # Reddit API 레이트 리밋 방지
                time.sleep(1)
                
            except Exception as e:
                print(f"Error collecting from r/{subreddit_name}: {e}")
    
    def collect_company_news(self, ticker: str, start_date: str, end_date: str, limit_per_subreddit: int = 1000):
        """
        특정 회사 관련 뉴스를 수집합니다.
        
        Args:
            ticker (str): 주식 티커
            start_date (str): 시작 날짜 (YYYY-MM-DD)
            end_date (str): 종료 날짜 (YYYY-MM-DD)
            limit_per_subreddit (int): 서브레딧당 수집할 포스트 수
        """
        print(f"Collecting company news for {ticker} from {start_date} to {end_date}")
        
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        for subreddit_name in self.categories["company_news"]:
            print(f"Processing subreddit: r/{subreddit_name}")
            
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # JSONL 파일 경로 - 티커를 파일명에 포함
                jsonl_file_path = os.path.join(
                    self.reddit_data_dir, 
                    "company_news", 
                    f"{subreddit_name}_{ticker}.jsonl"  # 티커 추가
                )
                
                posts_collected = []
                
                # new 정렬로 변경하여 최신 포스트부터 수집
                for post in subreddit.new(limit=limit_per_subreddit):
                    post_date = datetime.fromtimestamp(post.created_utc)
                    
                    # 날짜 범위 확인
                    if start_dt <= post_date <= end_dt:
                        # 회사 관련 포스트인지 확인
                        if self._is_company_related(post, ticker):
                            post_dict = self._post_to_dict(post)
                            posts_collected.append(post_dict)
                
                # JSONL 파일에 저장
                with open(jsonl_file_path, 'w', encoding='utf-8') as f:
                    for post_dict in posts_collected:
                        f.write(json.dumps(post_dict, ensure_ascii=False) + '\n')
                
                print(f"Collected {len(posts_collected)} {ticker}-related posts from r/{subreddit_name}")
                
                # Reddit API 레이트 리밋 방지
                time.sleep(1)
                
            except Exception as e:
                print(f"Error collecting from r/{subreddit_name}: {e}")
    
    def collect_global_news_monthly(self, year: int, month: int, limit_per_subreddit: int = 1000):
        """
        특정 년월의 글로벌 뉴스 데이터를 수집합니다.
        
        Args:
            year (int): 년도
            month (int): 월 (1-12)
            limit_per_subreddit (int): 서브레딧당 수집할 포스트 수
        """
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        print(f"Collecting global news for {year}-{month:02d}")
        
        for subreddit_name in self.categories["global_news"]:
            print(f"Processing subreddit: r/{subreddit_name}")
            
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # 월별 JSONL 파일 경로
                jsonl_file_path = os.path.join(
                    self.reddit_data_dir, 
                    "global_news", 
                    f"{subreddit_name}_{year}_{month:02d}.jsonl"
                )
                
                posts_collected = []
                
                # new 정렬로 변경하여 최신 포스트부터 수집
                for post in subreddit.new(limit=limit_per_subreddit):
                    post_date = datetime.fromtimestamp(post.created_utc)
                    
                    # 날짜 범위 확인
                    if start_date <= post_date <= end_date:
                        post_dict = self._post_to_dict(post)
                        posts_collected.append(post_dict)
                
                # JSONL 파일에 저장
                with open(jsonl_file_path, 'w', encoding='utf-8') as f:
                    for post_dict in posts_collected:
                        f.write(json.dumps(post_dict, ensure_ascii=False) + '\n')
                
                print(f"Collected {len(posts_collected)} posts from r/{subreddit_name} for {year}-{month:02d}")
                
                # Reddit API 레이트 리밋 방지
                time.sleep(1)
                
            except Exception as e:
                print(f"Error collecting from r/{subreddit_name}: {e}")
    
    def collect_company_news_monthly(self, ticker: str, year: int, month: int, limit_per_subreddit: int = 1000):
        """
        특정 년월의 회사 관련 뉴스를 수집합니다.
        
        Args:
            ticker (str): 주식 티커
            year (int): 년도
            month (int): 월 (1-12)
            limit_per_subreddit (int): 서브레딧당 수집할 포스트 수
        """
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        print(f"Collecting company news for {ticker} in {year}-{month:02d}")
        
        for subreddit_name in self.categories["company_news"]:
            print(f"Processing subreddit: r/{subreddit_name}")
            
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # 월별 JSONL 파일 경로
                jsonl_file_path = os.path.join(
                    self.reddit_data_dir, 
                    "company_news", 
                    f"{subreddit_name}_{ticker}_{year}_{month:02d}.jsonl"
                )
                
                posts_collected = []
                
                # new 정렬로 변경하여 최신 포스트부터 수집
                for post in subreddit.new(limit=limit_per_subreddit):
                    post_date = datetime.fromtimestamp(post.created_utc)
                    
                    # 날짜 범위 확인
                    if start_date <= post_date <= end_date:
                        # 회사 관련 포스트인지 확인
                        if self._is_company_related(post, ticker):
                            post_dict = self._post_to_dict(post)
                            posts_collected.append(post_dict)
                
                # JSONL 파일에 저장
                with open(jsonl_file_path, 'w', encoding='utf-8') as f:
                    for post_dict in posts_collected:
                        f.write(json.dumps(post_dict, ensure_ascii=False) + '\n')
                
                print(f"Collected {len(posts_collected)} {ticker}-related posts from r/{subreddit_name} for {year}-{month:02d}")
                
                # Reddit API 레이트 리밋 방지
                time.sleep(1)
                
            except Exception as e:
                print(f"Error collecting from r/{subreddit_name}: {e}")
    
    def collect_all_data(self, start_date: str, end_date: str, tickers: Optional[List[str]] = None):
        """
        모든 데이터를 수집합니다.
        
        Args:
            start_date (str): 시작 날짜 (YYYY-MM-DD)
            end_date (str): 종료 날짜 (YYYY-MM-DD)
            tickers (List[str]): 수집할 티커 리스트 (None이면 모든 티커)
        """
        print(f"Starting data collection from {start_date} to {end_date}")
        
        # 글로벌 뉴스 수집
        self.collect_global_news(start_date, end_date)
        
        # 회사별 뉴스 수집
        if tickers is None:
            tickers = list(self.ticker_to_company.keys())
        
        for ticker in tickers:
            print(f"\nCollecting data for {ticker}...")
            self.collect_company_news(ticker, start_date, end_date)
        
        print("Data collection completed!")

    def collect_all_data_monthly(self, start_year: int, start_month: int, end_year: int, end_month: int, tickers: Optional[List[str]] = None):
        """
        최신 데이터부터 과거 데이터까지 월별로 모든 데이터를 수집합니다.
        
        Args:
            start_year (int): 시작 년도
            start_month (int): 시작 월
            end_year (int): 종료 년도
            end_month (int): 종료 월
            tickers (List[str]): 수집할 티커 리스트 (None이면 모든 티커)
        """
        print(f"Starting monthly data collection from {end_year}-{end_month:02d} to {start_year}-{start_month:02d} (newest to oldest)")
        
        # 회사별 뉴스 수집
        if tickers is None:
            tickers = list(self.ticker_to_company.keys())
        
        current_year = end_year
        current_month = end_month
        
        while (current_year > start_year) or (current_year == start_year and current_month >= start_month):
            print(f"\n=== Processing {current_year}-{current_month:02d} ===")
            
            # 글로벌 뉴스 수집
            self.collect_global_news_monthly(current_year, current_month)
            
            # 회사별 뉴스 수집
            for ticker in tickers:
                print(f"\nCollecting data for {ticker} in {current_year}-{current_month:02d}...")
                self.collect_company_news_monthly(ticker, current_year, current_month)
            
            # 이전 월로 이동 (최신에서 과거로)
            current_month -= 1
            if current_month < 1:
                current_month = 12
                current_year -= 1
            
            # 월간 수집 완료 후 잠시 대기
            print(f"Completed {current_year}-{current_month+1:02d}, waiting 5 seconds...")
            time.sleep(5)
        
        print("Monthly data collection completed!")


def main():
    """
    메인 실행 함수
    """
    # Reddit API 설정 (실제 값으로 교체 필요)
    CLIENT_ID = "qqS6I80ZreAruZmbGw-Bxw"
    CLIENT_SECRET = "4P_iTwBTr4nn6Ij5WE1V3rop120HMA"
    USER_AGENT = "TradingAgents/1.0"
    
    # 데이터 수집기 초기화
    collector = RedditDataCollector(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT
    )
    
    # 현재부터 2008년 1월까지 월별 데이터 수집 (최신 데이터부터)
    current_date = datetime.now()
    collector.collect_all_data_monthly(
        start_year=2008,
        start_month=1,
        end_year=current_date.year,
        end_month=current_date.month
    )
    
    # 특정 기간만 수집하려면:
    # collector.collect_all_data_monthly(2020, 1, 2020, 12)
    
    # 특정 티커만 수집하려면:
    # collector.collect_all_data_monthly(2008, 1, current_date.year, current_date.month, tickers=["AAPL", "TSLA"])


if __name__ == "__main__":
    main() 