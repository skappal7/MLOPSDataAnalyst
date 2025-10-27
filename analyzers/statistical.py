"""Statistical Analyzer - Correlations, distributions, tests"""
from typing import List, Dict, Any
from core.duckdb_engine import DuckDBEngine
import scipy.stats as stats
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

class StatisticalAnalyzer:
    def __init__(self, parquet_path: str, config: Dict[str, Any]):
        self.engine = DuckDBEngine(parquet_path)
        self.config = config
        self.corr_threshold = 0.6
    
    def analyze(self) -> List[Dict[str, Any]]:
        """Run comprehensive statistical analysis."""
        insights = []
        
        metrics = self.config.get('key_metrics', [])
        
        # Correlation analysis
        if len(metrics) >= 2:
            insights.extend(self._analyze_correlations(metrics))
        
        # Distribution analysis
        insights.extend(self._analyze_distributions(metrics))
        
        # Summary statistics
        insights.extend(self._analyze_summary_stats(metrics))
        
        return insights
    
    def _analyze_correlations(self, metrics: List[str]) -> List[Dict[str, Any]]:
        """Analyze correlations between key metrics."""
        insights = []
        
        try:
            corr_df = self.engine.get_correlation_matrix(metrics)
            
            for row in corr_df.to_dicts():
                var1, var2 = row['var1'], row['var2']
                corr = row['correlation']
                
                # Skip self-correlations and weak correlations
                if var1 == var2 or abs(corr) < self.corr_threshold:
                    continue
                
                # Get sample data for visualization
                data = self.engine.query(f"""
                    SELECT {var1}, {var2} 
                    FROM data 
                    WHERE {var1} IS NOT NULL AND {var2} IS NOT NULL
                    LIMIT 1000
                """)
                
                # Calculate p-value with full dataset
                full_data = self.engine.query(f"""
                    SELECT {var1}, {var2} 
                    FROM data 
                    WHERE {var1} IS NOT NULL AND {var2} IS NOT NULL
                """).to_numpy()
                
                if len(full_data) > 3:
                    _, p_value = stats.pearsonr(full_data[:, 0], full_data[:, 1])
                else:
                    p_value = 1.0
                
                # Determine strength
                strength = self._get_correlation_strength(corr)
                direction = "positive" if corr > 0 else "negative"
                
                # Create scatter plot
                chart = self._create_scatter_plot(data, var1, var2, corr)
                
                # Score based on strength and significance
                score = abs(corr) * 7
                if p_value < 0.01:
                    score += 2
                elif p_value < 0.05:
                    score += 1
                
                insights.append({
                    'type': 'correlation',
                    'category': 'statistical',
                    'title': f"{strength.capitalize()} {direction} correlation: {var1} ↔ {var2}",
                    'data': {
                        'var1': var1,
                        'var2': var2,
                        'correlation': float(corr),
                        'p_value': float(p_value),
                        'strength': strength,
                        'direction': direction,
                        'significance': 'Highly significant' if p_value < 0.01 else 'Significant' if p_value < 0.05 else 'Not significant'
                    },
                    'chart': chart,
                    'raw_score': score
                })
        
        except Exception as e:
            print(f"Error in correlation analysis: {e}")
        
        return insights
    
    def _analyze_distributions(self, metrics: List[str]) -> List[Dict[str, Any]]:
        """Analyze distributions and test for normality."""
        insights = []
        
        for metric in metrics:
            try:
                # Get statistics
                stats_dict = self.engine.get_numeric_stats(metric)
                
                # Get sample for testing
                data = self.engine.query(f"""
                    SELECT {metric} 
                    FROM data 
                    WHERE {metric} IS NOT NULL
                """).to_numpy().flatten()
                
                if len(data) < 20:
                    continue
                
                # Test for normality (sample if too large)
                test_sample = data[:5000] if len(data) > 5000 else data
                statistic, p_value = stats.shapiro(test_sample)
                
                # Calculate skewness and kurtosis
                skewness = float(stats.skew(data))
                kurtosis = float(stats.kurtosis(data))
                
                # Only report if significantly non-normal
                if p_value < 0.05:
                    # Create histogram
                    chart = self._create_histogram(data, metric)
                    
                    # Determine distribution type
                    dist_type = self._classify_distribution(skewness, kurtosis)
                    
                    insights.append({
                        'type': 'distribution',
                        'category': 'statistical',
                        'title': f"{dist_type} distribution detected: {metric}",
                        'data': {
                            'metric': metric,
                            'test': 'Shapiro-Wilk',
                            'p_value': float(p_value),
                            'skewness': skewness,
                            'kurtosis': kurtosis,
                            'distribution_type': dist_type,
                            'mean': float(stats_dict.get('mean', 0)),
                            'median': float(stats_dict.get('median', 0)),
                            'std': float(stats_dict.get('std', 0))
                        },
                        'chart': chart,
                        'raw_score': 5.0 if abs(skewness) > 1 or abs(kurtosis) > 1 else 4.0
                    })
            
            except Exception as e:
                print(f"Error analyzing distribution for {metric}: {e}")
        
        return insights
    
    def _analyze_summary_stats(self, metrics: List[str]) -> List[Dict[str, Any]]:
        """Analyze summary statistics for unusual patterns."""
        insights = []
        
        for metric in metrics:
            try:
                stats_dict = self.engine.get_numeric_stats(metric)
                
                mean = stats_dict.get('mean', 0)
                median = stats_dict.get('median', 0)
                std = stats_dict.get('std', 0)
                
                # Check for high coefficient of variation
                if mean != 0:
                    cv = (std / abs(mean)) * 100
                    
                    if cv > 100:  # High variability
                        insights.append({
                            'type': 'variability',
                            'category': 'statistical',
                            'title': f"High variability in {metric}",
                            'data': {
                                'metric': metric,
                                'coefficient_of_variation': float(cv),
                                'mean': float(mean),
                                'std': float(std),
                                'interpretation': 'Data shows high dispersion relative to mean'
                            },
                            'raw_score': 5.5
                        })
                
                # Check for mean-median discrepancy (indicates skew)
                if median != 0:
                    discrepancy = abs((mean - median) / median) * 100
                    
                    if discrepancy > 20:
                        insights.append({
                            'type': 'skewness',
                            'category': 'statistical',
                            'title': f"Asymmetric distribution in {metric}",
                            'data': {
                                'metric': metric,
                                'mean': float(mean),
                                'median': float(median),
                                'discrepancy_pct': float(discrepancy),
                                'interpretation': 'Mean and median differ significantly'
                            },
                            'raw_score': 5.0
                        })
            
            except Exception as e:
                print(f"Error in summary stats for {metric}: {e}")
        
        return insights
    
    def _create_scatter_plot(self, data, var1: str, var2: str, corr: float):
        """Create scatter plot with trendline."""
        try:
            df = data.to_pandas()
            
            fig = px.scatter(
                df, x=var1, y=var2,
                title=f"{var1} vs {var2} (r={corr:.3f})",
                trendline="ols",
                opacity=0.6
            )
            
            fig.update_layout(
                template="plotly_white",
                height=400,
                showlegend=False
            )
            
            return fig
        except:
            return None
    
    def _create_histogram(self, data, metric: str):
        """Create histogram with normal curve overlay."""
        try:
            fig = go.Figure()
            
            # Histogram
            fig.add_trace(go.Histogram(
                x=data,
                name=metric,
                opacity=0.7,
                nbinsx=30
            ))
            
            fig.update_layout(
                title=f"Distribution of {metric}",
                xaxis_title=metric,
                yaxis_title="Frequency",
                template="plotly_white",
                height=400,
                showlegend=False
            )
            
            return fig
        except:
            return None
    
    @staticmethod
    def _get_correlation_strength(corr: float) -> str:
        """Classify correlation strength."""
        abs_corr = abs(corr)
        if abs_corr >= 0.9:
            return "very strong"
        elif abs_corr >= 0.7:
            return "strong"
        elif abs_corr >= 0.5:
            return "moderate"
        else:
            return "weak"
    
    @staticmethod
    def _classify_distribution(skewness: float, kurtosis: float) -> str:
        """Classify distribution type."""
        if abs(skewness) < 0.5 and abs(kurtosis) < 0.5:
            return "Normal"
        elif skewness > 1:
            return "Right-skewed"
        elif skewness < -1:
            return "Left-skewed"
        elif kurtosis > 1:
            return "Heavy-tailed"
        elif kurtosis < -1:
            return "Light-tailed"
        else:
            return "Non-normal"
