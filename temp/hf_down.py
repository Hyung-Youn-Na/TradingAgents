from huggingface_hub import hf_hub_download
import pandas as pd
import pyarrow.parquet as pq

# 1. Hugging Face에서 Parquet 파일 다운로드
parquet_path = hf_hub_download(
    repo_id="sehyun66/Finnhub-News",
    repo_type="dataset",
    filename="data/train-00000-of-00001-ce680d7056476977.parquet"  # 실제 파일명 확인 필요 시 변경
)

# 2. Parquet 파일을 PyArrow로 읽고 Pandas DataFrame으로 변환
table = pq.read_table(parquet_path)
df = table.to_pandas()

# 3. 컬럼명 확인
print("기존 컬럼명:")
print(df.columns.tolist())

# 4. 컬럼명 정리 (필요 시 수정)
df.rename(columns={
    "related": "related",
    "datetime": "datetime",
    "image": "image",
    "url": "url",
    "headline": "headline",
    "sentiment_name": "sentiment_name",
    "source": "source",
    "sentiment": "sentiment",
    "summary": "summary",
    "id": "id",
    "category": "category"
}, inplace=True)

# 5. 정리된 DataFrame 일부 출력
print("정리된 데이터:")
print(df.head())

# 6. CSV로 저장
df.to_csv("finnhub_news_clean.csv", index=False)
print("CSV 저장 완료: finnhub_news_clean.csv")