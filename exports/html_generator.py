"""HTML Generator"""
from typing import List, Dict, Any

class HTMLGenerator:
    def generate(self, insights: List[Dict[str, Any]], config: Dict[str, Any]) -> str:
        """Generate HTML report."""
        return "<html><body><h1>Analysis Report</h1></body></html>"
