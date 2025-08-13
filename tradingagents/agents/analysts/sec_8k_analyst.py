from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def create_sec_8k_analyst(llm, toolkit):
    def sec_8k_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        tools = [toolkit.get_sec_edgar_8k_analysis]

        system_message = (
            """You are a SEC 8-K Current Report analyst. Analyze material events disclosed in 8-K filings and focus on:

- Nature of events (M&A, leadership changes, material contracts, earnings releases)
- Estimated immediate and short-term impact on the stock
- Any compliance issues or regulatory concerns

Provide an immediate-impact summary suitable for trading response, and add a brief Markdown table of the key events and implications."""
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
            "sec_8k_report": report,
        }

    return sec_8k_analyst_node


