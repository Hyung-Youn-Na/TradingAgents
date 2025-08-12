# 1. Import the library
from edgar import *

# 2. Tell the SEC who you are (required by SEC regulations)
set_identity("your.name@example.com")  # Replace with your email

# 3. Find a company
company = Company("AAPL")  # Apple

# 4. Get company filings
filings = company.get_filings() 

# 5. Filter by form 
# insider_filings = filings.filter(form="8-K", filing_date="2024-01-01:2024-12-31")  # 8-K Report
# insider_filings = filings.filter(form="10-Q", filing_date="2024-01-01:2024-12-31")  # 10-Q Report

# filing date {start_date}:{end_date}인데 start date가 비어있을 경우 처음 파일링 부터 다 가져옴 start date를 비우고 end date를 입력후 가장 최신거를 가져오면 될듯

latest_ten_k_filing = filings.filter(form="10-K", filing_date=":2024-12-31").latest()  # 10-K Report
latest_ten_q_filing = filings.filter(form="10-Q", filing_date=":2024-12-31").latest()  # 10-Q Report
latest_eight_k_filing = filings.filter(form="8-K", filing_date=":2024-12-31").latest()  # 8-K Report

# 7. Convert to a data object
tenk_object = latest_ten_k_filing.obj()
tenq_object = latest_ten_q_filing.obj()
eightk_object = latest_eight_k_filing.obj()


# data of each filing

import pdb; pdb.set_trace()
# 10-K
tenk_balance_sheet = tenk_object.balance_sheet.render().to_markdown()
tenk_income_statement = tenk_object.income_statement.render().to_markdown()
tenk_cash_flow = tenk_object.cash_flow_statement.render().to_markdown()
tenk_management_discussion = tenk_object.management_discussion
tenk_risk_factors = tenk_object.risk_factors



# 10-Q
tenq_PARTI_ITEM1 = tenq_object.get_item_with_part("PART I", "ITEM 1")
tenq_PARTI_ITEM2 = tenq_object.get_item_with_part("PART I", "ITEM 2")
tenq_PARTI_ITEM3 = tenq_object.get_item_with_part("PART I", "ITEM 3")
tenq_PARTI_ITEM4 = tenq_object.get_item_with_part("PART I", "ITEM 4")
tenq_PARTI_ITEM5 = tenq_object.get_item_with_part("PART I", "ITEM 5")
tenq_PARTI_ITEM6 = tenq_object.get_item_with_part("PART I", "ITEM 6")
tenq_PARTII_ITEM1 = tenq_object.get_item_with_part("PART II", "ITEM 1")
tenq_PARTII_ITEM1A = tenq_object.get_item_with_part("PART II", "ITEM 1A")
tenq_PARTII_ITEM2 = tenq_object.get_item_with_part("PART II", "ITEM 2")
tenq_PARTII_ITEM3 = tenq_object.get_item_with_part("PART II", "ITEM 3")
tenq_PARTII_ITEM4 = tenq_object.get_item_with_part("PART II", "ITEM 4")
tenq_PARTII_ITEM5 = tenq_object.get_item_with_part("PART II", "ITEM 5")
tenq_PARTII_ITEM6 = tenq_object.get_item_with_part("PART II", "ITEM 6")

# 8-K
eightk_text = eightk_object.text.render().to_markdown()







