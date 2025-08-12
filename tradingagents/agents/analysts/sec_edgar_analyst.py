from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from datetime import datetime, timedelta


def create_sec_edgar_analyst(llm, toolkit):
    def sec_edgar_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        # Calculate date range for analysis (1 year back from current date)
        current_date_obj = datetime.strptime(current_date, "%Y-%m-%d")
        start_date = (current_date_obj - timedelta(days=365)).strftime("%Y-%m-%d")
        end_date = current_date

        if toolkit.config["online_tools"]:
            tools = [
                toolkit.get_sec_edgar_10k_analysis,
                toolkit.get_sec_edgar_10q_analysis,
                toolkit.get_sec_edgar_8k_analysis,
            ]
        else:
            tools = [
                toolkit.get_sec_edgar_10k_analysis,
                toolkit.get_sec_edgar_10q_analysis,
                toolkit.get_sec_edgar_8k_analysis,
            ]

        system_message = (
            """You are a SEC EDGAR filing analyst tasked with analyzing financial reports and regulatory filings for a company. Your role is to provide comprehensive analysis of the following SEC filings:

10-K Annual Report Analysis:
- Balance Sheet: Analyze assets, liabilities, and shareholders' equity trends
- Income Statement: Review revenue, expenses, and profitability metrics
- Cash Flow Statement: Examine operating, investing, and financing cash flows
- Management Discussion & Analysis (MD&A): Evaluate management's perspective on business performance
- Risk Factors: Assess identified risks and their potential impact

10-Q Quarterly Report Analysis:
- Financial Performance: Compare quarterly results with previous periods
- Business Updates: Review management's discussion of recent developments
- Risk Assessment: Identify any new or changed risk factors
- Forward-Looking Statements: Analyze projections and guidance

8-K Current Report Analysis:
- Material Events: Review significant corporate events and their implications
- Financial Results: Analyze earnings releases and financial updates
- Corporate Actions: Assess mergers, acquisitions, leadership changes, etc.
- Regulatory Compliance: Review any compliance-related disclosures

Key Analysis Areas:
1. Financial Health: Evaluate liquidity, solvency, and profitability trends
2. Business Performance: Assess revenue growth, market position, and competitive advantages
3. Risk Assessment: Identify material risks and their potential impact on stock price
4. Management Quality: Evaluate management's transparency and strategic decisions
5. Regulatory Compliance: Review adherence to SEC requirements and any violations
6. Forward-Looking Indicators: Analyze guidance, projections, and strategic initiatives

Please provide detailed, nuanced analysis that goes beyond surface-level observations. Focus on:
- Quantitative trends and their implications
- Qualitative factors affecting business performance
- Comparative analysis with industry peers when relevant
- Risk-reward assessment for investors
- Specific insights that could impact trading decisions

Write a comprehensive report that synthesizes all filing information into actionable insights for traders and investors. Do not simply state trends are mixed; provide detailed and fine-grained analysis with specific examples and data points."""
            + """ Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read."""
        )

        # system_message = (
        #     """Write a comprehensive report that synthesizes all filing information into actionable insights for traders and investors. Do not simply state trends are mixed; provide detailed and fine-grained analysis with specific examples and data points."""
        #     + """ Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read."""
        # )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    "For your reference, the current date is {current_date}. The company we want to analyze is {ticker}. "
                    "For filing analysis, use start_date: {start_date} and end_date: {end_date} to get relevant filings.",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)
        prompt = prompt.partial(start_date=start_date)
        prompt = prompt.partial(end_date=end_date)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke({"messages": state["messages"]})

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content
       
        return {
            "messages": [result],
            "sec_edgar_report": report,
        }

    return sec_edgar_analyst_node
