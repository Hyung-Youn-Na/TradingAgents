from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def create_sec_10q_analyst(llm, toolkit):
    def sec_10q_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        tools = [toolkit.get_sec_edgar_10q_analysis]

        system_message = (
            """You are a SEC 10-Q Quarterly Report analyst. Analyze the company's recent 10-Q filings and focus on:

- Quarterly performance vs prior quarter and prior year
- Segment performance, margins, guidance updates
- New or changed risk factors and short-term liquidity

Provide crisp, actionable insights relevant for near-term trading, and end with a compact Markdown table of the key points."""
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
            "sec_10q_report": report,
        }

    return sec_10q_analyst_node


