"""Markdown Generator"""
from typing import List, Dict, Any

class MarkdownGenerator:
    def generate(self, insights: List[Dict[str, Any]], config: Dict[str, Any]) -> str:
        """Generate Markdown report."""
        md = "# Analysis Report\n\n"
        md += "## Key Findings\n\n"
        
        for idx, insight in enumerate(insights[:10], 1):
            md += f"### {idx}. {insight.get('title', 'Insight')}\n"
            md += f"{insight.get('narrative', 'No details')}\n\n"
        
        return md
