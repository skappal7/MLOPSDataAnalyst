"""Insight Scorer"""
from typing import List, Dict, Any

class InsightScorer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def score_all(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score and rank insights."""
        for insight in insights:
            insight['score'] = self._calculate_score(insight)
        
        return sorted(insights, key=lambda x: x['score'], reverse=True)
    
    def _calculate_score(self, insight: Dict[str, Any]) -> float:
        """Calculate insight score (0-10)."""
        raw_score = insight.get('raw_score', 5.0)
        return min(raw_score, 10.0)
