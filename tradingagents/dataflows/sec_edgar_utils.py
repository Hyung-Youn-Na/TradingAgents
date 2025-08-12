# SEC EDGAR data utilities

from edgar import *
from typing import Annotated, Callable, Any, Optional, Dict, List
from pandas import DataFrame
import pandas as pd
from functools import wraps
import json
from datetime import datetime, timedelta
import re

from .utils import save_output, SavePathType, decorate_all_methods


def validate_date_format(date_str: str) -> bool:
    """Validate date format is YYYY-MM-DD"""
    if not date_str:
        return True
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    return bool(re.match(pattern, date_str))


def safe_render_to_markdown(obj, default_text: str = "Data not available") -> str:
    """Safely render object to markdown with error handling"""
    try:
        if hasattr(obj, 'render') and callable(obj.render):
            rendered = obj.render()
            if hasattr(rendered, 'to_markdown') and callable(rendered.to_markdown):
                return rendered.to_markdown()
            else:
                return str(rendered)
        else:
            return str(obj.text) if obj else default_text
    except Exception as e:
        return f"{default_text} (Error: {str(e)})"


def safe_get_item(obj, part: str, item: str, default: str = "Not available") -> str:
    """Safely get item from 10-Q object with error handling"""
    try:
        if hasattr(obj, 'get_item_with_part') and callable(obj.get_item_with_part):
            result = obj.get_item_with_part(part, item)
            return str(result) if result else default
        else:
            return default
    except Exception as e:
        return f"{default} (Error: {str(e)})"


class SECEdgarUtils:
    
    def __init__(self, email: str = "your.email@example.com"):
        """Initialize SEC EDGAR utilities with user email for SEC compliance"""
        self.email = email
        try:
            set_identity(email)
        except Exception as e:
            print(f"Warning: Failed to set identity with email {email}: {str(e)}")
    
    def _get_company(self, symbol: str):
        """Helper method to get Company object with error handling"""
        try:
            return Company(symbol)
        except Exception as e:
            raise Exception(f"Failed to initialize company for symbol {symbol}: {str(e)}")
    
    def get_company_info(
        self,
        symbol: Annotated[str, "ticker symbol"],
        save_path: Optional[str] = None,
    ) -> Dict:
        """Fetches and returns company information from SEC EDGAR."""
        try:
            company = self._get_company(symbol)
            company_info = {
                "Company Name": getattr(company, 'name', 'N/A'),
                "CIK": getattr(company, 'cik', 'N/A'),
                "SIC": getattr(company, 'sic', 'N/A'),
                "Industry": getattr(company, 'industry', 'N/A'),
                "State": getattr(company, 'state', 'N/A'),
                "Country": getattr(company, 'country', 'N/A'),
            }
            
            if save_path:
                with open(save_path, 'w') as f:
                    json.dump(company_info, f, indent=2)
                print(f"Company info for {company.cik} saved to {save_path}")
            
            return company_info
        except Exception as e:
            return {
                "error": f"Failed to get company info: {str(e)}",
                "symbol": symbol
            }
    
    def get_filing_summary(
        self,
        symbol: Annotated[str, "ticker symbol"],
        filing_type: Annotated[str, "type of filing (10-K, 10-Q, 8-K, etc.)"] = "all",
        start_date: Annotated[str, "start date in YYYY-MM-DD format"] = None,
        end_date: Annotated[str, "end date in YYYY-MM-DD format"] = None,
        limit: Annotated[int, "maximum number of filings to return"] = 10,
        save_path: SavePathType = None,
    ) -> DataFrame:
        """Get a summary of recent SEC filings for a company."""
        try:
            # Validate date formats
            if start_date and not validate_date_format(start_date):
                return DataFrame([{"error": f"Invalid start_date format: {start_date}. Use YYYY-MM-DD format."}])
            if end_date and not validate_date_format(end_date):
                return DataFrame([{"error": f"Invalid end_date format: {end_date}. Use YYYY-MM-DD format."}])
            
            company = self._get_company(symbol)
            filings = company.get_filings()
            
            # Filter filings by type and date
            if filing_type.lower() != "all":
                if start_date and end_date:
                    filing_filter = filings.filter(form=filing_type, filing_date=f"{start_date}:{end_date}")
                elif end_date:
                    filing_filter = filings.filter(form=filing_type, filing_date=f":{end_date}")
                else:
                    filing_filter = filings.filter(form=filing_type)
            else:
                if start_date and end_date:
                    filing_filter = filings.filter(filing_date=f"{start_date}:{end_date}")
                elif end_date:
                    filing_filter = filings.filter(filing_date=f":{end_date}")
                else:
                    filing_filter = filings
            
            # Get recent filings
            recent_filings = filing_filter.head(limit)
            
            # Convert to DataFrame
            filing_data = []
            for filing in recent_filings:
                filing_data.append({
                    "form": getattr(filing, 'form', 'N/A'),
                    "filing_date": getattr(filing, 'filing_date', 'N/A'),
                    "period_of_report": getattr(filing, 'period_of_report', 'N/A'),
                    "accession_number": getattr(filing, 'accession_number', 'N/A'),
                    "description": getattr(filing, 'description', 'N/A'),
                    "company_name": getattr(company, 'name', 'N/A'),
                    "cik": getattr(company, 'cik', 'N/A')
                })
            
            df = DataFrame(filing_data)
            
            if save_path:
                save_output(df, f"SEC filings for {company.cik}", save_path)
            
            return df
        except Exception as e:
            return DataFrame([{"error": f"Failed to get filing summary: {str(e)}", "symbol": symbol}])
    
    def get_latest_10k(
        self,
        symbol: Annotated[str, "ticker symbol"],
        end_date: Annotated[str, "end date in YYYY-MM-DD format"] = None,
        save_path: SavePathType = None,
    ) -> Dict:
        """Get the latest 10-K annual report for a company."""
        try:
            # Validate date format
            if end_date and not validate_date_format(end_date):
                return {"error": f"Invalid end_date format: {end_date}. Use YYYY-MM-DD format."}
            
            company = self._get_company(symbol)
            filings = company.get_filings()
            
            # Get latest 10-K
            if end_date:
                latest_10k = filings.filter(form="10-K", filing_date=f":{end_date}").latest()
            else:
                latest_10k = filings.filter(form="10-K").latest()
            
            tenk_object = latest_10k.obj()
            
            # Extract key financial data with safe rendering
            result = {
                "filing_date": getattr(latest_10k, 'filing_date', 'N/A'),
                "period_of_report": getattr(latest_10k, 'period_of_report', 'N/A'),
                "accession_number": getattr(latest_10k, 'accession_number', 'N/A'),
                "company_name": getattr(company, 'name', 'N/A'),
                "cik": getattr(company, 'cik', 'N/A'),
                "balance_sheet": safe_render_to_markdown(getattr(tenk_object, 'balance_sheet', None)),
                "income_statement": safe_render_to_markdown(getattr(tenk_object, 'income_statement', None)),
                "cash_flow": safe_render_to_markdown(getattr(tenk_object, 'cash_flow_statement', None)),
                "management_discussion": getattr(tenk_object, 'management_discussion', 'Not available'),
                "risk_factors": getattr(tenk_object, 'risk_factors', 'Not available'),
            }
            
            if save_path:
                with open(save_path, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                print(f"10-K data for {company.cik} saved to {save_path}")
            
            return result
        except Exception as e:
            return {"error": f"Failed to get 10-K data: {str(e)}", "symbol": symbol}
    
    def get_latest_10q(
        self,
        symbol: Annotated[str, "ticker symbol"],
        end_date: Annotated[str, "end date in YYYY-MM-DD format"] = None,
        save_path: SavePathType = None,
    ) -> Dict:
        """Get the latest 10-Q quarterly report for a company."""
        try:
            # Validate date format
            if end_date and not validate_date_format(end_date):
                return {"error": f"Invalid end_date format: {end_date}. Use YYYY-MM-DD format."}
            
            company = self._get_company(symbol)
            filings = company.get_filings()
            
            # Get latest 10-Q
            if end_date:
                latest_10q = filings.filter(form="10-Q", filing_date=f":{end_date}").latest()
            else:
                latest_10q = filings.filter(form="10-Q").latest()
            
            tenq_object = latest_10q.obj()
            
            # Extract key sections with safe item retrieval
            result = {
                "filing_date": getattr(latest_10q, 'filing_date', 'N/A'),
                "period_of_report": getattr(latest_10q, 'period_of_report', 'N/A'),
                "accession_number": getattr(latest_10q, 'accession_number', 'N/A'),
                "company_name": getattr(company, 'name', 'N/A'),
                "cik": getattr(company, 'cik', 'N/A'),
                "part1_item1": safe_get_item(tenq_object, "PART I", "ITEM 1"),
                "part1_item2": safe_get_item(tenq_object, "PART I", "ITEM 2"),
                "part1_item3": safe_get_item(tenq_object, "PART I", "ITEM 3"),
                "part1_item4": safe_get_item(tenq_object, "PART I", "ITEM 4"),
                "part1_item5": safe_get_item(tenq_object, "PART I", "ITEM 5"),
                "part1_item6": safe_get_item(tenq_object, "PART I", "ITEM 6"),
                "part2_item1": safe_get_item(tenq_object, "PART II", "ITEM 1"),
                "part2_item1a": safe_get_item(tenq_object, "PART II", "ITEM 1A"),
                "part2_item2": safe_get_item(tenq_object, "PART II", "ITEM 2"),
                "part2_item3": safe_get_item(tenq_object, "PART II", "ITEM 3"),
                "part2_item4": safe_get_item(tenq_object, "PART II", "ITEM 4"),
                "part2_item5": safe_get_item(tenq_object, "PART II", "ITEM 5"),
                "part2_item6": safe_get_item(tenq_object, "PART II", "ITEM 6"),
            }
            
            if save_path:
                with open(save_path, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                print(f"10-Q data for {company.cik} saved to {save_path}")
            
            return result
        except Exception as e:
            return {"error": f"Failed to get 10-Q data: {str(e)}", "symbol": symbol}
    
    def get_latest_8k(
        self,
        symbol: Annotated[str, "ticker symbol"],
        end_date: Annotated[str, "end date in YYYY-MM-DD format"] = None,
        save_path: SavePathType = None,
    ) -> Dict:
        """Get the latest 8-K current report for a company."""
        try:
            # Validate date format
            if end_date and not validate_date_format(end_date):
                return {"error": f"Invalid end_date format: {end_date}. Use YYYY-MM-DD format."}
            
            company = self._get_company(symbol)
            filings = company.get_filings()
            
            # Get latest 8-K
            if end_date:
                latest_8k = filings.filter(form="8-K", filing_date=f":{end_date}").latest()
            else:
                latest_8k = filings.filter(form="8-K").latest()
            
            eightk_object = latest_8k.obj()
            
            result = {
                "filing_date": getattr(latest_8k, 'filing_date', 'N/A'),
                "period_of_report": getattr(latest_8k, 'period_of_report', 'N/A'),
                "accession_number": getattr(latest_8k, 'accession_number', 'N/A'),
                "company_name": getattr(company, 'name', 'N/A'),
                "cik": getattr(company, 'cik', 'N/A'),
                "text": eightk_object.text(),
            }
            if save_path:
                with open(save_path, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                print(f"8-K data for {company.cik} saved to {save_path}")
            
            return result
        except Exception as e:
            return {"error": f"Failed to get 8-K data: {str(e)}", "symbol": symbol}
    
    def get_financial_metrics(
        self,
        symbol: Annotated[str, "ticker symbol"],
        end_date: Annotated[str, "end date in YYYY-MM-DD format"] = None,
        save_path: SavePathType = None,
    ) -> DataFrame:
        """Extract key financial metrics from latest 10-K and 10-Q filings."""
        try:
            # Validate date format
            if end_date and not validate_date_format(end_date):
                return DataFrame([{"error": f"Invalid end_date format: {end_date}. Use YYYY-MM-DD format."}])
            
            company = self._get_company(symbol)
            
            # Get latest 10-K and 10-Q with error handling
            tenk_data = self.get_latest_10k(symbol, end_date)
            tenq_data = self.get_latest_10q(symbol, end_date)
            
            # Check for errors in the data
            if "error" in tenk_data:
                return DataFrame([{"error": f"10-K error: {tenk_data['error']}"}])
            if "error" in tenq_data:
                return DataFrame([{"error": f"10-Q error: {tenq_data['error']}"}])
            
            # Extract key metrics
            metrics = {
                "company_name": getattr(company, 'name', 'N/A'),
                "cik": getattr(company, 'cik', 'N/A'),
                "latest_10k_date": tenk_data.get("filing_date", 'N/A'),
                "latest_10q_date": tenq_data.get("filing_date", 'N/A'),
                "10k_period": tenk_data.get("period_of_report", 'N/A'),
                "10q_period": tenq_data.get("period_of_report", 'N/A'),
            }
            
            df = DataFrame([metrics])
            
            if save_path:
                save_output(df, f"Financial metrics for {company.cik}", save_path)
            
            return df
        except Exception as e:
            return DataFrame([{"error": f"Failed to get financial metrics: {str(e)}", "symbol": symbol}])
