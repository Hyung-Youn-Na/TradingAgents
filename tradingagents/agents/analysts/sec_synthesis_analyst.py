from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def create_sec_synthesis_analyst(llm):
    def sec_synthesis_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        system_message = (
            """You are the SEC Synthesis Analyst. Integrate insights across 10-K, 10-Q, and 8-K analyses to produce:

1) A unified fundamental/near-term view
2) Key risks and mitigants
3) A clear risk-reward and scenario analysis
4) Actionable investment thesis and catalysts

End with a crisp Markdown table: thesis bullets, risk bullets, and timeframes (short/medium/long)."""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants. "
                    "Synthesize across available reports to form a final, actionable perspective.\n"
                    "{system_message}\nCurrent date: {current_date}. Ticker: {ticker}.",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm
        result = chain.invoke({"messages": state["messages"]})

        report = result.content

        return {
            "messages": [result],
            "sec_synthesis_report": report,
        }

    return sec_synthesis_analyst_node


