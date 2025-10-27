"""Categorical Analyzer - Segment analysis, chi-square tests"""
from typing import List, Dict, Any
from core.duckdb_engine import DuckDBEngine
import scipy.stats as stats
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

class CategoricalAnalyzer:
    def __init__(self, parquet_path: str, config: Dict[str, Any]):
        self.engine = DuckDBEngine(parquet_path)
        self.config = config
        self.profile = config.get('profile', {})
    
    def analyze(self) -> List[Dict[str, Any]]:
        """Analyze categorical dimensions."""
        insights = []
        
        categorical_cols = self.profile.get('categorical_columns', [])
        metrics = self.config.get('key_metrics', [])
        
        # Segment comparison for each metric
        for cat_col in categorical_cols[:5]:  # Limit to top 5 categorical columns
            for metric in metrics:
                insights.extend(self._analyze_segment_performance(cat_col, metric))
        
        # Concentration analysis
        for cat_col in categorical_cols[:3]:
            insights.extend(self._analyze_concentration(cat_col))
        
        return insights
    
    def _analyze_segment_performance(self, segment_col: str, metric: str) -> List[Dict[str, Any]]:
        """Compare metric performance across segments."""
        insights = []
        
        try:
            # Get segment comparison
            segment_data = self.engine.get_segment_comparison(segment_col, metric, 'AVG')
            
            if len(segment_data) < 2:
                return []
            
            df = segment_data.to_pandas()
            
            # Calculate overall statistics
            overall_mean = df['metric_value'].mean()
            overall_std = df['metric_value'].std()
            
            # Find top and bottom performers
            top_segment = df.nlargest(1, 'metric_value').iloc[0]
            bottom_segment = df.nsmallest(1, 'metric_value').iloc[0]
            
            # Calculate performance gap
            gap_pct = ((top_segment['metric_value'] - bottom_segment['metric_value']) / 
                      bottom_segment['metric_value'] * 100) if bottom_segment['metric_value'] != 0 else 0
            
            # Only report significant gaps
            if abs(gap_pct) > 30:
                # Create bar chart
                chart = self._create_segment_chart(df, segment_col, metric)
                
                # Perform ANOVA to test significance
                segments = []
                for seg in df['segment'].unique():
                    seg_data = self.engine.query(f"""
                        SELECT {metric} 
                        FROM data 
                        WHERE {segment_col} = '{seg}' AND {metric} IS NOT NULL
                        LIMIT 1000
                    """).to_numpy().flatten()
                    
                    if len(seg_data) > 0:
                        segments.append(seg_data)
                
                if len(segments) >= 2:
                    f_stat, p_value = stats.f_oneway(*segments)
                else:
                    f_stat, p_value = 0, 1.0
                
                # Score based on gap size and significance
                score = 6.0 + (min(abs(gap_pct) / 20, 3))
                if p_value < 0.05:
                    score += 1
                
                insights.append({
                    'type': 'segment_divergence',
                    'category': 'categorical',
                    'title': f"Significant performance gap in {metric} across {segment_col}",
                    'data': {
                        'dimension': segment_col,
                        'metric': metric,
                        'top_segment': str(top_segment['segment']),
                        'top_value': float(top_segment['metric_value']),
                        'bottom_segment': str(bottom_segment['segment']),
                        'bottom_value': float(bottom_segment['metric_value']),
                        'gap_percentage': float(gap_pct),
                        'p_value': float(p_value),
                        'significance': 'Significant' if p_value < 0.05 else 'Not significant'
                    },
                    'chart': chart,
                    'raw_score': score
                })
        
        except Exception as e:
            print(f"Error in segment analysis for {segment_col}, {metric}: {e}")
        
        return insights
    
    def _analyze_concentration(self, cat_col: str) -> List[Dict[str, Any]]:
        """Analyze concentration in categorical variables."""
        insights = []
        
        try:
            # Get distribution
            dist = self.engine.get_categorical_distribution(cat_col, top_n=20)
            
            if len(dist) < 2:
                return []
            
            df = dist.to_pandas()
            
            # Calculate concentration metrics
            total = df['count'].sum()
            top_3_pct = df.head(3)['percentage'].sum()
            top_5_pct = df.head(5)['percentage'].sum()
            
            # Herfindahl index (concentration measure)
            herfindahl = sum((df['percentage'] / 100) ** 2)
            
            # Report high concentration
            if top_3_pct > 70:
                chart = self._create_concentration_chart(df, cat_col)
                
                insights.append({
                    'type': 'high_concentration',
                    'category': 'categorical',
                    'title': f"High concentration in {cat_col}",
                    'data': {
                        'dimension': cat_col,
                        'top_3_percentage': float(top_3_pct),
                        'top_5_percentage': float(top_5_pct),
                        'herfindahl_index': float(herfindahl),
                        'num_categories': len(df),
                        'interpretation': 'High concentration may indicate dependency risk'
                    },
                    'chart': chart,
                    'raw_score': 6.5 if top_3_pct > 80 else 5.5
                })
        
        except Exception as e:
            print(f"Error in concentration analysis for {cat_col}: {e}")
        
        return insights
    
    def _create_segment_chart(self, df, segment_col: str, metric: str):
        """Create bar chart for segment comparison."""
        try:
            fig = px.bar(
                df.sort_values('metric_value', ascending=False),
                x='segment',
                y='metric_value',
                title=f"{metric} by {segment_col}",
                labels={'segment': segment_col, 'metric_value': metric}
            )
            
            fig.update_layout(
                template="plotly_white",
                height=400,
                xaxis_tickangle=-45
            )
            
            return fig
        except:
            return None
    
    def _create_concentration_chart(self, df, cat_col: str):
        """Create pie chart for concentration."""
        try:
            # Take top 10 and group rest
            top_df = df.head(10).copy()
            if len(df) > 10:
                others_pct = df.iloc[10:]['percentage'].sum()
                others_row = {'category': 'Others', 'percentage': others_pct, 'count': df.iloc[10:]['count'].sum()}
                import pandas as pd
                top_df = pd.concat([top_df, pd.DataFrame([others_row])], ignore_index=True)
            
            fig = px.pie(
                top_df,
                values='percentage',
                names='category',
                title=f"Distribution of {cat_col}"
            )
            
            fig.update_layout(
                template="plotly_white",
                height=400
            )
            
            return fig
        except:
            return None
