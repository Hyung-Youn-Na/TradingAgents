import pandas as pd
import yfinance as yf
import os
from datetime import datetime, timedelta


def download_stock_data(
    symbol: str,
    start_date: str = None,
    end_date: str = None,
    years_back: int = 5,
    output_dir: str = "data_temp"
):
    """
    Yahoo Finance에서 주식 데이터를 다운로드하고 CSV 파일로 저장합니다.
    
    Args:
        symbol (str): 주식 심볼 (예: 'AAPL', 'MSFT', '005930.KS')
        start_date (str): 시작 날짜 (YYYY-MM-DD 형식, None이면 years_back 사용)
        end_date (str): 종료 날짜 (YYYY-MM-DD 형식, None이면 오늘 날짜 사용)
        years_back (int): 몇 년 전부터 데이터를 가져올지 (start_date가 None일 때 사용)
        output_dir (str): CSV 파일을 저장할 디렉토리
    """
    
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    # 날짜 설정
    if end_date is None:
        end_date = datetime.now()
    else:
        end_date = pd.to_datetime(end_date)
    
    if start_date is None:
        start_date = end_date - timedelta(days=365 * years_back)
    else:
        start_date = pd.to_datetime(start_date)
    
    # 날짜를 문자열로 변환
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    print(f"다운로드 중: {symbol}")
    print(f"기간: {start_str} ~ {end_str}")
    
    try:
        # Yahoo Finance에서 데이터 다운로드
        data = yf.download(
            symbol,
            start=start_str,
            end=end_str,
            progress=True,
            auto_adjust=True,
            multi_level_index=False
        )
        
        if data.empty:
            print(f"경고: {symbol}에 대한 데이터를 찾을 수 없습니다.")
            return None
        
        # 인덱스를 컬럼으로 변환
        data = data.reset_index()
        
        # 파일명 생성
        filename = f"{symbol}-YFin-data-{start_str}-{end_str}.csv"
        filepath = os.path.join(output_dir, filename)
        
        # CSV 파일로 저장
        data.to_csv(filepath, index=False)
        print(f"데이터가 저장되었습니다: {filepath}")
        print(f"데이터 형태: {data.shape}")
        print(f"컬럼: {list(data.columns)}")
        
        return data
        
    except Exception as e:
        print(f"오류 발생: {e}")
        return None


def download_multiple_stocks(
    symbols: list,
    start_date: str = None,
    end_date: str = None,
    years_back: int = 5,
    output_dir: str = "temp"
):
    """
    여러 주식 심볼의 데이터를 일괄 다운로드합니다.
    
    Args:
        symbols (list): 주식 심볼 리스트
        start_date (str): 시작 날짜
        end_date (str): 종료 날짜
        years_back (int): 몇 년 전부터 데이터를 가져올지
        output_dir (str): CSV 파일을 저장할 디렉토리
    """
    
    results = {}
    
    for symbol in symbols:
        print(f"\n{'='*50}")
        data = download_stock_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            years_back=years_back,
            output_dir=output_dir
        )
        results[symbol] = data
    
    return results


if __name__ == "__main__":
    # 사용 예시
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'TSM', 'JPM', 'JNJ', 'V', 'WMT', 'META']
    # 1. 단일 주식 다운로드
    # print("=== 단일 주식 다운로드 예시 ===")
    # download_stock_data("META", years_back=15)
    download_multiple_stocks(tickers, years_back=15)
