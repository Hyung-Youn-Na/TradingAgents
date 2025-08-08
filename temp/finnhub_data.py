import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
from tqdm import tqdm
import pandas as pd

class FinnhubDataDownloader:
    """
    Finnhub API를 통해 데이터를 다운로드하고 프로젝트의 오프라인 데이터 구조에 맞게 저장하는 클래스
    """
    
    def __init__(self, api_key: str, data_dir: str = "/mnt/trading_agents/data"):
        """
        Args:
            api_key (str): Finnhub API 키
            data_dir (str): 데이터 저장 디렉토리
        """
        self.api_key = api_key
        self.base_url = "https://finnhub.io/api/v1"
        self.data_dir = data_dir
        self.finnhub_data_dir = os.path.join(data_dir, "finnhub_data")
        
        # 데이터 타입별 디렉토리 생성
        self.data_types = [
            "news_data",
            "insider_trans", 
            "insider_senti",
            "SEC_filings",
            "fin_as_reported"
        ]
        
        self._create_directories()
    
    def _create_directories(self):
        """필요한 디렉토리들을 생성합니다."""
        for data_type in self.data_types:
            type_dir = os.path.join(self.finnhub_data_dir, data_type)
            os.makedirs(type_dir, exist_ok=True)
    
    def _make_api_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Finnhub API 요청을 수행합니다.
        
        Args:
            endpoint (str): API 엔드포인트
            params (Dict): 요청 파라미터
            
        Returns:
            Dict: API 응답 데이터
        """
        if params is None:
            params = {}
        
        params['token'] = self.api_key
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, params=params, timeout=30)
            
            # 응답 상태 코드 확인
            if response.status_code == 200:
                # 응답이 비어있는지 확인
                if response.text.strip():
                    return response.json()
                else:
                    print(f"빈 응답: {url}")
                    return {}
            else:
                print(f"HTTP 오류 {response.status_code}: {response.text}")
                return {}
                
        except requests.exceptions.RequestException as e:
            print(f"API 요청 실패: {e}")
            return {}
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}")
            print(f"응답 내용: {response.text[:200]}...")
            return {}
    
    def download_company_news(self, symbol: str, start_date: str, end_date: str) -> Dict:
        """
        회사 뉴스 데이터를 다운로드합니다.
        Finnhub API 문서에 따르면: /company-news?symbol=AAPL&from=2025-01-15&to=2025-02-20
        
        Args:
            symbol (str): 주식 심볼 (예: AAPL)
            start_date (str): 시작 날짜 (YYYY-MM-DD)
            end_date (str): 종료 날짜 (YYYY-MM-DD)
            
        Returns:
            Dict: 날짜별 뉴스 데이터
        """
        print(f"{symbol} 뉴스 데이터 다운로드 중...")
        
        # API 요청 - 문서에 따른 정확한 엔드포인트 사용
        params = {
            'symbol': symbol,
            'from': start_date,
            'to': end_date
        }
        
        response = self._make_api_request('company-news', params)
        
        # 날짜별로 데이터 정리
        news_data = {}
        if response:
            for news_item in response:
                # datetime을 날짜로 변환
                if 'datetime' in news_item:
                    # UNIX timestamp를 datetime으로 변환
                    dt = datetime.fromtimestamp(news_item['datetime'])
                    date_key = dt.strftime("%Y-%m-%d")
                    
                    if date_key not in news_data:
                        news_data[date_key] = []
                    news_data[date_key].append(news_item)
        
        return news_data
    
    def download_insider_transactions(self, symbol: str, start_date: str, end_date: str) -> Dict:
        """
        내부자 거래 데이터를 다운로드합니다.
        
        Args:
            symbol (str): 주식 심볼
            start_date (str): 시작 날짜 (YYYY-MM-DD)
            end_date (str): 종료 날짜 (YYYY-MM-DD)
            
        Returns:
            Dict: 날짜별 내부자 거래 데이터
        """
        print(f"{symbol} 내부자 거래 데이터 다운로드 중...")
        
        # API 요청
        params = {
            'symbol': symbol,
            'from': start_date,
            'to': end_date
        }
        
        response = self._make_api_request('stock/insider-transactions', params)
        
        # 날짜별로 데이터 정리
        insider_data = {}
        if response and 'data' in response:
            for transaction in response['data']:
                filing_date = transaction.get('filingDate', '')
                if filing_date:
                    date_key = filing_date[:10]  # YYYY-MM-DD 형식으로 추출
                    if date_key not in insider_data:
                        insider_data[date_key] = []
                    insider_data[date_key].append(transaction)
        
        return insider_data
    
    def download_insider_sentiment(self, symbol: str, start_date: str, end_date: str) -> Dict:
        """
        내부자 센티먼트 데이터를 다운로드합니다.
        
        Args:
            symbol (str): 주식 심볼
            start_date (str): 시작 날짜 (YYYY-MM-DD)
            end_date (str): 종료 날짜 (YYYY-MM-DD)
            
        Returns:
            Dict: 날짜별 내부자 센티먼트 데이터
        """
        print(f"{symbol} 내부자 센티먼트 데이터 다운로드 중...")
        
        # API 요청
        params = {
            'symbol': symbol,
            'from': start_date,
            'to': end_date
        }
        
        response = self._make_api_request('stock/insider-sentiment', params)
        
        # 날짜별로 데이터 정리
        sentiment_data = {}
        if response and 'data' in response:
            for item in response['data']:
                year = item.get('year', '')
                month = item.get('month', '')
                if year and month:
                    date_key = f"{year}-{month:02d}-01"  # 월별 데이터를 첫째 날로 매핑
                    if date_key not in sentiment_data:
                        sentiment_data[date_key] = []
                    sentiment_data[date_key].append(item)
        
        return sentiment_data
    
    def download_sec_filings(self, symbol: str, start_date: str, end_date: str) -> Dict:
        """
        SEC 제출 데이터를 다운로드합니다.
        
        Args:
            symbol (str): 주식 심볼
            start_date (str): 시작 날짜 (YYYY-MM-DD)
            end_date (str): 종료 날짜 (YYYY-MM-DD)
            
        Returns:
            Dict: 날짜별 SEC 제출 데이터
        """
        print(f"{symbol} SEC 제출 데이터 다운로드 중...")
        
        # API 요청
        params = {
            'symbol': symbol,
            'from': start_date,
            'to': end_date
        }
        
        response = self._make_api_request('stock/filings', params)
        
        # 날짜별로 데이터 정리
        filings_data = {}
        if response and 'data' in response:
            for filing in response['data']:
                filing_date = filing.get('filingDate', '')
                if filing_date:
                    date_key = filing_date[:10]  # YYYY-MM-DD 형식으로 추출
                    if date_key not in filings_data:
                        filings_data[date_key] = []
                    filings_data[date_key].append(filing)
        
        return filings_data
    
    def download_financial_reported(self, symbol: str, start_date: str, end_date: str) -> Dict:
        """
        재무 데이터를 다운로드합니다.
        
        Args:
            symbol (str): 주식 심볼
            start_date (str): 시작 날짜 (YYYY-MM-DD)
            end_date (str): 종료 날짜 (YYYY-MM-DD)
            
        Returns:
            Dict: 날짜별 재무 데이터
        """
        print(f"{symbol} 재무 데이터 다운로드 중...")
        
        # API 요청
        params = {
            'symbol': symbol,
            'from': start_date,
            'to': end_date
        }
        
        response = self._make_api_request('stock/financial-reported', params)
        
        # 날짜별로 데이터 정리
        financial_data = {}
        if response and 'data' in response:
            for item in response['data']:
                report_date = item.get('reportDate', '')
                if report_date:
                    date_key = report_date[:10]  # YYYY-MM-DD 형식으로 추출
                    if date_key not in financial_data:
                        financial_data[date_key] = []
                    financial_data[date_key].append(item)
        
        return financial_data
    
    def save_data(self, symbol: str, data_type: str, data: Dict, period: str = None):
        """
        데이터를 프로젝트 구조에 맞게 저장합니다.
        
        Args:
            symbol (str): 주식 심볼
            data_type (str): 데이터 타입
            data (Dict): 저장할 데이터
            period (str): 기간 (annual/quarterly, 선택사항)
        """
        if period:
            filename = f"{symbol}_{period}_data_formatted.json"
        else:
            filename = f"{symbol}_data_formatted.json"
        
        filepath = os.path.join(self.finnhub_data_dir, data_type, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"{symbol} {data_type} 데이터가 {filepath}에 저장되었습니다.")
    
    def download_all_data_for_symbol(self, symbol: str, start_date: str, end_date: str):
        """
        특정 심볼에 대한 모든 Finnhub 데이터를 다운로드합니다.
        
        Args:
            symbol (str): 주식 심볼
            start_date (str): 시작 날짜 (YYYY-MM-DD)
            end_date (str): 종료 날짜 (YYYY-MM-DD)
        """
        print(f"\n=== {symbol} 데이터 다운로드 시작 ===")
        
        # 1. 뉴스 데이터
        news_data = self.download_company_news(symbol, start_date, end_date)
        self.save_data(symbol, "news_data", news_data)
        
        # 2. 내부자 거래 데이터
        insider_trans_data = self.download_insider_transactions(symbol, start_date, end_date)
        self.save_data(symbol, "insider_trans", insider_trans_data)
        
        # 3. 내부자 센티먼트 데이터
        insider_senti_data = self.download_insider_sentiment(symbol, start_date, end_date)
        self.save_data(symbol, "insider_senti", insider_senti_data)
        
        # 4. SEC 제출 데이터
        sec_filings_data = self.download_sec_filings(symbol, start_date, end_date)
        self.save_data(symbol, "SEC_filings", sec_filings_data)
        
        # 5. 재무 데이터
        financial_data = self.download_financial_reported(symbol, start_date, end_date)
        self.save_data(symbol, "fin_as_reported", financial_data)
        
        print(f"\n=== {symbol} 데이터 다운로드 완료 ===")
    
    def download_data_for_multiple_symbols(self, symbols: List[str], start_date: str, end_date: str):
        """
        여러 심볼에 대한 데이터를 일괄 다운로드합니다.
        
        Args:
            symbols (List[str]): 주식 심볼 리스트
            start_date (str): 시작 날짜 (YYYY-MM-DD)
            end_date (str): 종료 날짜 (YYYY-MM-DD)
        """
        print(f"\n=== {len(symbols)}개 심볼 데이터 일괄 다운로드 시작 ===")
        
        for symbol in symbols:
            try:
                self.download_all_data_for_symbol(symbol, start_date, end_date)
                print(f"{symbol} 완료")
            except Exception as e:
                print(f"{symbol} 오류: {e}")
            
            # API 레이트 리밋 방지
            time.sleep(1)
        
        print(f"\n=== 일괄 다운로드 완료 ===")


def main():
    """
    메인 실행 함수
    """
    # Finnhub API 키 설정 (환경변수에서 가져오거나 직접 입력)
    api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        api_key = input("Finnhub API 키를 입력하세요: ")
    
    # API 키 유효성 검사
    print(f"API 키: {api_key[:10]}...")
    
    # 데이터 다운로더 초기화
    downloader = FinnhubDataDownloader(api_key)
    
    # 다운로드할 심볼과 날짜 범위 설정
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]  # 예시 심볼들
    start_date = "2024-01-01"
    end_date = "2024-12-31"
    
    # 단일 심볼 다운로드 예시
    # downloader.download_all_data_for_symbol("AAPL", start_date, end_date)
    
    # 여러 심볼 일괄 다운로드
    downloader.download_data_for_multiple_symbols(symbols, start_date, end_date)


if __name__ == "__main__":
    main()
