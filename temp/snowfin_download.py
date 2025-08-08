import pandas as pd

# Login using e.g. `huggingface-cli login` to access this dataset
df = pd.read_parquet("hf://datasets/snorkelai/agent-finance-reasoning/train.parquet")

df.to_csv("snowfin_train.csv", index=False)