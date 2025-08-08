import finnhub
import json
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Finnhub 클라이언트 초기화
finnhub_client = finnhub.Client(api_key="d1m7ek9r01qvvurkjf00d1m7ek9r01qvvurkjf0g")

# 데이터 저장 경로 설정
DATA_DIR = "/mnt/trading_agents/finnhub"
FINNHUB_DATA_DIR = os.path.join(DATA_DIR, "finnhub_data")

# 필요한 디렉토리 생성
os.makedirs(os.path.join(FINNHUB_DATA_DIR, "news_data"), exist_ok=True)
os.makedirs(os.path.join(FINNHUB_DATA_DIR, "insider_trans"), exist_ok=True)
os.makedirs(os.path.join(FINNHUB_DATA_DIR, "insider_senti"), exist_ok=True)
os.makedirs(os.path.join(FINNHUB_DATA_DIR, "SEC_filings"), exist_ok=True)

def download_and_save_finnhub_data(ticker, start_date, end_date):
    """
    Finnhub API를 사용해서 데이터를 다운로드하고 지정된 포맷으로 저장
    """
    print(f"Downloading data for {ticker} from {start_date} to {end_date}")
    
    # 1. SEC Filings 데이터 다운로드
    print("Downloading SEC filings...")
    try:
        SEC_filings_data = finnhub_client.filings(symbol=ticker, _from=start_date, to=end_date)
        
        # SEC filings 데이터를 날짜별로 그룹화
        filings_by_date = {}
        for filing in SEC_filings_data:
            date_str = filing.get('filingDate', '')[:10]  # YYYY-MM-DD 형식
            if date_str not in filings_by_date:
                filings_by_date[date_str] = []
            filings_by_date[date_str].append(filing)
        
        # JSON 파일로 저장
        sec_file_path = os.path.join(FINNHUB_DATA_DIR, "SEC_filings", f"{ticker}_data_formatted.json")
        with open(sec_file_path, 'w') as f:
            json.dump(filings_by_date, f, indent=2)
        print(f"SEC filings saved to {sec_file_path}")
        
    except Exception as e:
        print(f"Error downloading SEC filings: {e}")
    
    # 2. 뉴스 데이터 다운로드
    print("Downloading news data...")
    try:
        news_data = finnhub_client.company_news(ticker, _from=start_date, to=end_date)
        
        # API 응답 확인 및 처리
        if isinstance(news_data, dict) and 'data' in news_data:
            news_data = news_data['data']
        elif not isinstance(news_data, list):
            print(f"Unexpected news data format: {type(news_data)}")
            news_data = []
        
        # 뉴스 데이터를 날짜별로 그룹화
        news_by_date = {}
        for news in news_data:
            if isinstance(news, dict):
                datetime_str = news.get('datetime', '')
                if isinstance(datetime_str, int):
                    # Unix timestamp를 문자열로 변환
                    datetime_str = str(datetime.fromtimestamp(datetime_str))
                date_str = datetime_str[:10]  # YYYY-MM-DD 형식
                if date_str and date_str != 'None':
                    if date_str not in news_by_date:
                        news_by_date[date_str] = []
                    news_by_date[date_str].append(news)
        
        # JSON 파일로 저장
        news_file_path = os.path.join(FINNHUB_DATA_DIR, "news_data", f"{ticker}_data_formatted.json")
        with open(news_file_path, 'w') as f:
            json.dump(news_by_date, f, indent=2)
        print(f"News data saved to {news_file_path}")
        
    except Exception as e:
        print(f"Error downloading news data: {e}")
        print(f"News data type: {type(news_data) if 'news_data' in locals() else 'Not available'}")
    
    # 3. 내부자 거래 데이터 다운로드
    print("Downloading insider transactions...")
    try:
        insider_transactions_data = finnhub_client.stock_insider_transactions(ticker, start_date, end_date)
        
        # API 응답 확인 및 처리
        if isinstance(insider_transactions_data, dict) and 'data' in insider_transactions_data:
            insider_transactions_data = insider_transactions_data['data']
        elif isinstance(insider_transactions_data, str):
            print(f"Insider transactions returned string: {insider_transactions_data}")
            insider_transactions_data = []
        elif not isinstance(insider_transactions_data, list):
            print(f"Unexpected insider transactions format: {type(insider_transactions_data)}")
            insider_transactions_data = []
        
        # 내부자 거래 데이터를 날짜별로 그룹화
        transactions_by_date = {}
        for transaction in insider_transactions_data:
            if isinstance(transaction, dict):
                date_str = transaction.get('filingDate', '')[:10]  # YYYY-MM-DD 형식
                if date_str and date_str != 'None':
                    if date_str not in transactions_by_date:
                        transactions_by_date[date_str] = []
                    transactions_by_date[date_str].append(transaction)
        
        # JSON 파일로 저장
        insider_trans_file_path = os.path.join(FINNHUB_DATA_DIR, "insider_trans", f"{ticker}_data_formatted.json")
        with open(insider_trans_file_path, 'w') as f:
            json.dump(transactions_by_date, f, indent=2)
        print(f"Insider transactions saved to {insider_trans_file_path}")
        
    except Exception as e:
        print(f"Error downloading insider transactions: {e}")
        print(f"Insider transactions data type: {type(insider_transactions_data) if 'insider_transactions_data' in locals() else 'Not available'}")
    
    # 4. 내부자 감정 데이터 다운로드
    print("Downloading insider sentiment...")
    try:
        insider_sentiment_data = finnhub_client.stock_insider_sentiment(ticker, start_date, end_date)
        
        # API 응답 확인 및 처리
        if isinstance(insider_sentiment_data, dict) and 'data' in insider_sentiment_data:
            insider_sentiment_data = insider_sentiment_data['data']
        elif isinstance(insider_sentiment_data, str):
            print(f"Insider sentiment returned string: {insider_sentiment_data}")
            insider_sentiment_data = []
        elif not isinstance(insider_sentiment_data, list):
            print(f"Unexpected insider sentiment format: {type(insider_sentiment_data)}")
            insider_sentiment_data = []
        
        # 내부자 감정 데이터를 날짜별로 그룹화
        sentiment_by_date = {}
        for sentiment in insider_sentiment_data:
            if isinstance(sentiment, dict):
                # sentiment 데이터는 월별로 제공되므로 월별로 그룹화
                year = sentiment.get('year', '')
                month = sentiment.get('month', '')
                if year and month:
                    year_month = f"{year}-{month:02d}"
                    if year_month not in sentiment_by_date:
                        sentiment_by_date[year_month] = []
                    sentiment_by_date[year_month].append(sentiment)
        
        # JSON 파일로 저장
        insider_sentiment_file_path = os.path.join(FINNHUB_DATA_DIR, "insider_senti", f"{ticker}_data_formatted.json")
        with open(insider_sentiment_file_path, 'w') as f:
            json.dump(sentiment_by_date, f, indent=2)
        print(f"Insider sentiment saved to {insider_sentiment_file_path}")
        
    except Exception as e:
        print(f"Error downloading insider sentiment: {e}")
        print(f"Insider sentiment data type: {type(insider_sentiment_data) if 'insider_sentiment_data' in locals() else 'Not available'}")

def download_multiple_tickers(tickers, start_date, end_date):
    """
    여러 티커에 대해 데이터를 다운로드
    """
    for ticker in tickers:
        print(f"\n{'='*50}")
        print(f"Processing {ticker}")
        print(f"{'='*50}")
        download_and_save_finnhub_data(ticker, start_date, end_date)

# 실행 예시
if __name__ == "__main__":
    # 다운로드할 티커 리스트
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'TSM', 'JPM', 'JNJ', 'V', 'WMT', 'META']
    
    # 날짜 범위 설정 (2010년부터 현재까지)
    start_date = "2010-07-21"
    end_date = "2025-07-21"
    
    # 데이터 다운로드 실행
    download_multiple_tickers(tickers, start_date, end_date)
    
    print("\nData download completed!")