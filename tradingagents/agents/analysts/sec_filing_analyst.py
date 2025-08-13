from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from edgar import *

@dataclass
class FilingAnalysisResult:
    """SEC filing 분석 결과를 저장하는 데이터 클래스"""
    company_ticker: str
    filing_type: str
    filing_date: str
    analysis_type: str
    data: Any
    success: bool
    error_message: Optional[str] = None

class SECFilingToolkit:
    """SEC filing 데이터를 분석하는 도구 모음"""
    
    def __init__(self, email: str, timeout: int = 30):
        """
        SEC Filing Toolkit 초기화
        
        Args:
            email: SEC 규정에 따라 필요한 이메일 주소
            timeout: 타임아웃 설정 (초)
        """
        self.email = email
        self.timeout = timeout
        set_identity(email)
        
    def get_company_filings(self, ticker: str, form_type: str = None, 
                          start_date: str = None, end_date: str = None) -> List:
        """
        회사의 SEC filing 목록을 가져옴
        
        Args:
            ticker: 회사 티커 심볼 (예: "AAPL")
            form_type: filing 타입 (예: "10-K", "10-Q", "8-K")
            start_date: 시작 날짜 (YYYY-MM-DD 형식)
            end_date: 종료 날짜 (YYYY-MM-DD 형식)
            
        Returns:
            filing 목록
        """
        try:
            company = Company(ticker)
            filings = company.get_filings()
            
            # 필터링 조건 구성
            filter_params = {}
            if form_type:
                filter_params["form"] = form_type
            if start_date and end_date:
                filter_params["filing_date"] = f"{start_date}:{end_date}"
            elif start_date:
                filter_params["filing_date"] = f"{start_date}:"
            elif end_date:
                filter_params["filing_date"] = f":{end_date}"
                
            if filter_params:
                filings = filings.filter(**filter_params)
                
            return filings
        except Exception as e:
            print(f"Error getting filings for {ticker}: {str(e)}")
            return []
    
    def analyze_10k_filing(self, ticker: str, filing_index: int = 0, 
                          start_date: str = None, end_date: str = None) -> FilingAnalysisResult:
        """
        10-K filing 분석 (연간 보고서)
        
        Args:
            ticker: 회사 티커
            filing_index: 가져올 filing 인덱스 (기본값: 0, 가장 최신)
            start_date: 시작 날짜
            end_date: 종료 날짜
            
        Returns:
            FilingAnalysisResult 객체
        """
        try:
            # 10-K filing 가져오기
            filings = self.get_company_filings(ticker, "10-K", start_date, end_date)
            
            if not filings:
                return FilingAnalysisResult(
                    company_ticker=ticker,
                    filing_type="10-K",
                    filing_date="",
                    analysis_type="financial_statements",
                    data=None,
                    success=False,
                    error_message="No 10-K filings found"
                )
            
            filing = filings[filing_index]
            ownership = filing.obj()
            
            # 재무제표 데이터 추출
            analysis_data = {
                "balance_sheet": None,
                "income_statement": None,
                "cash_flow_statement": None,
                "management_discussion": None,
                "risk_factors": None
            }
            
            # 재무상태표
            try:
                balance_sheet = ownership.balance_sheet.render()
                analysis_data["balance_sheet"] = balance_sheet.to_markdown() if hasattr(balance_sheet, 'to_markdown') else str(balance_sheet)
            except Exception as e:
                analysis_data["balance_sheet"] = f"Error: {str(e)}"
            
            # 손익계산서
            try:
                income_statement = ownership.income_statement.render()
                analysis_data["income_statement"] = income_statement.to_markdown() if hasattr(income_statement, 'to_markdown') else str(income_statement)
            except Exception as e:
                analysis_data["income_statement"] = f"Error: {str(e)}"
            
            # 현금흐름표
            try:
                cash_flow = ownership.cash_flow_statement.render()
                analysis_data["cash_flow_statement"] = cash_flow.to_markdown() if hasattr(cash_flow, 'to_markdown') else str(cash_flow)
            except Exception as e:
                analysis_data["cash_flow_statement"] = f"Error: {str(e)}"
            
            # 경영진 논의 및 분석
            try:
                analysis_data["management_discussion"] = str(ownership.management_discussion)
            except Exception as e:
                analysis_data["management_discussion"] = f"Error: {str(e)}"
            
            # 위험 요소
            try:
                analysis_data["risk_factors"] = str(ownership.risk_factors)
            except Exception as e:
                analysis_data["risk_factors"] = f"Error: {str(e)}"
            
            return FilingAnalysisResult(
                company_ticker=ticker,
                filing_type="10-K",
                filing_date=str(filing.filing_date),
                analysis_type="financial_statements",
                data=analysis_data,
                success=True
            )
            
        except Exception as e:
            return FilingAnalysisResult(
                company_ticker=ticker,
                filing_type="10-K",
                filing_date="",
                analysis_type="financial_statements",
                data=None,
                success=False,
                error_message=str(e)
            )
    
    def analyze_10q_filing(self, ticker: str, filing_index: int = 0,
                          start_date: str = None, end_date: str = None) -> FilingAnalysisResult:
        """
        10-Q filing 분석 (분기 보고서)
        
        Args:
            ticker: 회사 티커
            filing_index: 가져올 filing 인덱스
            start_date: 시작 날짜
            end_date: 종료 날짜
            
        Returns:
            FilingAnalysisResult 객체
        """
        try:
            filings = self.get_company_filings(ticker, "10-Q", start_date, end_date)
            
            if not filings:
                return FilingAnalysisResult(
                    company_ticker=ticker,
                    filing_type="10-Q",
                    filing_date="",
                    analysis_type="quarterly_report",
                    data=None,
                    success=False,
                    error_message="No 10-Q filings found"
                )
            
            filing = filings[filing_index]
            ownership = filing.obj()
            
            # 10-Q 섹션별 데이터 추출
            analysis_data = {
                "part1_items": {},
                "part2_items": {}
            }
            
            # PART I - Item 1~4
            part1_items = ["Item 1", "Item 2", "Item 3", "Item 4"]
            for item in part1_items:
                try:
                    # 타임아웃 설정으로 무한 대기 방지
                    item_data = self._get_item_with_timeout(ownership, "PART I", item)
                    analysis_data["part1_items"][item] = item_data
                except Exception as e:
                    analysis_data["part1_items"][item] = f"Error: {str(e)}"
            
            # PART II - Item 1, 1A, 2~6
            part2_items = ["Item 1", "Item 1A", "Item 2", "Item 3", "Item 4", "Item 5", "Item 6"]
            for item in part2_items:
                try:
                    item_data = self._get_item_with_timeout(ownership, "PART II", item)
                    analysis_data["part2_items"][item] = item_data
                except Exception as e:
                    analysis_data["part2_items"][item] = f"Error: {str(e)}"
            
            return FilingAnalysisResult(
                company_ticker=ticker,
                filing_type="10-Q",
                filing_date=str(filing.filing_date),
                analysis_type="quarterly_report",
                data=analysis_data,
                success=True
            )
            
        except Exception as e:
            return FilingAnalysisResult(
                company_ticker=ticker,
                filing_type="10-Q",
                filing_date="",
                analysis_type="quarterly_report",
                data=None,
                success=False,
                error_message=str(e)
            )
    
    def analyze_8k_filing(self, ticker: str, filing_index: int = 0,
                         start_date: str = None, end_date: str = None) -> FilingAnalysisResult:
        """
        8-K filing 분석 (중요 사건 보고서)
        
        Args:
            ticker: 회사 티커
            filing_index: 가져올 filing 인덱스
            start_date: 시작 날짜
            end_date: 종료 날짜
            
        Returns:
            FilingAnalysisResult 객체
        """
        try:
            filings = self.get_company_filings(ticker, "8-K", start_date, end_date)
            
            if not filings:
                return FilingAnalysisResult(
                    company_ticker=ticker,
                    filing_type="8-K",
                    filing_date="",
                    analysis_type="current_report",
                    data=None,
                    success=False,
                    error_message="No 8-K filings found"
                )
            
            filing = filings[filing_index]
            ownership = filing.obj()
            
            # 8-K 텍스트 내용 추출
            try:
                filing_text = ownership.text()
                analysis_data = {
                    "filing_text": filing_text,
                    "filing_date": str(filing.filing_date),
                    "form_type": filing.form
                }
            except Exception as e:
                analysis_data = {
                    "filing_text": f"Error extracting text: {str(e)}",
                    "filing_date": str(filing.filing_date),
                    "form_type": filing.form
                }
            
            return FilingAnalysisResult(
                company_ticker=ticker,
                filing_type="8-K",
                filing_date=str(filing.filing_date),
                analysis_type="current_report",
                data=analysis_data,
                success=True
            )
            
        except Exception as e:
            return FilingAnalysisResult(
                company_ticker=ticker,
                filing_type="8-K",
                filing_date="",
                analysis_type="current_report",
                data=None,
                success=False,
                error_message=str(e)
            )
    
    def _get_item_with_timeout(self, ownership, part: str, item: str) -> str:
        """
        타임아웃을 설정하여 특정 아이템을 가져오는 헬퍼 함수
        
        Args:
            ownership: filing 객체
            part: 파트 (예: "PART I", "PART II")
            item: 아이템 (예: "Item 1", "Item 2")
            
        Returns:
            아이템 내용 또는 에러 메시지
        """
        try:
            # 비동기로 실행하여 타임아웃 설정
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def get_item_async():
                return ownership.get_item_with_part(part, item)
            
            # 타임아웃 설정
            result = asyncio.wait_for(get_item_async(), timeout=self.timeout)
            return str(result)
            
        except asyncio.TimeoutError:
            return f"Timeout after {self.timeout} seconds"
        except Exception as e:
            return f"Error: {str(e)}"
        finally:
            loop.close()

def create_sec_filing_analyst(llm, toolkit):
    """SEC Filing Analyst 생성 함수"""
    
    # SEC Filing Toolkit 초기화 (이메일은 설정에서 가져와야 함)
    sec_toolkit = SECFilingToolkit("your.email@example.com")  # TODO: 설정에서 가져오기
    
    def sec_filing_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        
        # SEC filing 분석 도구들
        tools = [
            sec_toolkit.analyze_10k_filing,
            sec_toolkit.analyze_10q_filing,
            sec_toolkit.analyze_8k_filing,
            sec_toolkit.get_company_filings
        ]

        system_message = (
            "You are a SEC filing analyst tasked with analyzing official SEC filings for a company. "
            "Your role is to provide comprehensive analysis of the company's SEC filings including: "
            "1. 10-K Annual Reports: Analyze financial statements, management discussion, and risk factors "
            "2. 10-Q Quarterly Reports: Analyze quarterly financial performance and business updates "
            "3. 8-K Current Reports: Analyze important events and material information "
            "Please provide detailed insights from these official documents to help traders understand "
            "the company's financial health, business performance, and any material developments. "
            "Focus on key financial metrics, trends, risks, and opportunities revealed in the filings. "
            "Make sure to append a Markdown table at the end of the report to organize key points "
            "from the SEC filings, organized and easy to read."
        )

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
                    "For your reference, the current date is {current_date}. The company we want to look at is {ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.__name__ for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke({"messages": state["messages"]})

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "sec_filing_report": report,
        }

    return sec_filing_analyst_node 