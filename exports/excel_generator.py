"""Excel Generator"""
from typing import List, Dict, Any
from io import BytesIO
import openpyxl

class ExcelGenerator:
    def generate(self, insights: List[Dict[str, Any]], config: Dict[str, Any]) -> bytes:
        """Generate Excel report."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Summary"
        ws['A1'] = "Analysis Report"
        
        output = BytesIO()
        wb.save(output)
        return output.getvalue()
