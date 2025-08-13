from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def create_sec_10k_analyst(llm, toolkit):
    def sec_10k_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        tools = [toolkit.get_sec_edgar_10k_analysis]

        system_message = (
            """You are a SEC 10-K Annual Report analyst. Analyze the company's most recent 10-K filings and focus on:

- Balance Sheet: assets, liabilities, shareholders' equity trends
- Income Statement: revenue growth, margins, and profitability trends
- Cash Flow Statement: sustainability of operating cash flow, investing and financing activities
- MD&A: management's narrative and strategy
- Risk Factors: material risks and how they may impact valuation

Deliver a concise yet comprehensive analysis with quantitative and qualitative insights, highlighting signals relevant for trading decisions. Conclude with a compact Markdown table of key findings."""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants. "
                    "Use the provided tools to progress towards answering the question. "
                    "If you cannot fully answer, another assistant will continue. "
                    "Tools: {tool_names}.\n{system_message}\nCurrent date: {current_date}. Ticker: {ticker}.",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke({"messages": state["messages"]})

        report = ""
        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "sec_10k_report": report,
        }

    return sec_10k_analyst_node


