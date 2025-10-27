"""Time Series Analyzer - Trends, seasonality, forecasting"""
from typing import List, Dict, Any
from core.duckdb_engine import DuckDBEngine
import scipy.stats as stats
import numpy as np
import plotly.graph_objects as go
from scipy import signal

class TimeSeriesAnalyzer:
    def __init__(self, parquet_path: str, config: Dict[str, Any]):
        self.engine = DuckDBEngine(parquet_path)
        self.config = config
    
    def analyze(self) -> List[Dict[str, Any]]:
        """Analyze time series patterns."""
        insights = []
        
        time_col = self.config.get('time_column')
        if not time_col:
            return insights
        
        metrics = self.config.get('key_metrics', [])
        granularity = self.config.get('time_granularity', 'Monthly').lower()
        
        for metric in metrics:
            insights.extend(self._analyze_trend(time_col, metric, granularity))
            insights.extend(self._analyze_growth_rates(time_col, metric, granularity))
            insights.extend(self._detect_volatility(time_col, metric, granularity))
        
        return insights
    
    def _analyze_trend(self, time_col: str, metric: str, granularity: str) -> List[Dict[str, Any]]:
        """Detect and analyze trends."""
        insights = []
        
        try:
            # Get time series data
            ts_data = self.engine.get_time_series_aggregation(
                time_col, metric, 'AVG', granularity
            )
            
            if len(ts_data) < 5:
                return []
            
            df = ts_data.to_pandas()
            values = df['value'].values
            
            # Remove NaN values
            valid_mask = ~np.isnan(values)
            values = values[valid_mask]
            
            if len(values) < 5:
                return []
            
            # Linear regression for trend
            x = np.arange(len(values))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
            
            # Only report significant trends
            if p_value < 0.05:
                trend_type = "upward" if slope > 0 else "downward"
                strength = "strong" if abs(r_value) > 0.7 else "moderate"
                
                # Calculate percentage change per period
                if intercept != 0:
                    pct_change_per_period = (slope / abs(intercept)) * 100
                else:
                    pct_change_per_period = 0
                
                # Create trend chart
                chart = self._create_trend_chart(df, metric, slope, intercept)
                
                # Score based on strength and significance
                score = 6.0 + (abs(r_value) * 3)
                if p_value < 0.01:
                    score += 1
                
                insights.append({
                    'type': 'trend',
                    'category': 'time_series',
                    'title': f"{strength.capitalize()} {trend_type} trend in {metric}",
                    'data': {
                        'metric': metric,
                        'trend': trend_type,
                        'strength': strength,
                        'slope': float(slope),
                        'r_squared': float(r_value ** 2),
                        'p_value': float(p_value),
                        'pct_change_per_period': float(pct_change_per_period)
                    },
                    'chart': chart,
                    'raw_score': score
                })
        
        except Exception as e:
            print(f"Error in trend analysis for {metric}: {e}")
        
        return insights
    
    def _analyze_growth_rates(self, time_col: str, metric: str, granularity: str) -> List[Dict[str, Any]]:
        """Analyze period-over-period growth rates."""
        insights = []
        
        try:
            growth_data = self.engine.calculate_growth_rate(time_col, metric, granularity)
            
            if len(growth_data) < 3:
                return []
            
            df = growth_data.to_pandas()
            growth_rates = df['growth_rate_pct'].dropna().values
            
            if len(growth_rates) < 3:
                return []
            
            # Calculate statistics
            avg_growth = np.mean(growth_rates)
            std_growth = np.std(growth_rates)
            
            # Find significant changes
            threshold = self.config.get('change_threshold', 0.15) * 100
            
            # Check for acceleration/deceleration
            recent_growth = np.mean(growth_rates[-3:]) if len(growth_rates) >= 3 else growth_rates[-1]
            earlier_growth = np.mean(growth_rates[:3]) if len(growth_rates) >= 6 else np.mean(growth_rates)
            
            growth_change = recent_growth - earlier_growth
            
            if abs(growth_change) > threshold:
                change_type = "acceleration" if growth_change > 0 else "deceleration"
                
                insights.append({
                    'type': 'growth_change',
                    'category': 'time_series',
                    'title': f"Growth {change_type} detected in {metric}",
                    'data': {
                        'metric': metric,
                        'change_type': change_type,
                        'recent_growth_rate': float(recent_growth),
                        'earlier_growth_rate': float(earlier_growth),
                        'change': float(growth_change),
                        'avg_growth_rate': float(avg_growth),
                        'volatility': float(std_growth)
                    },
                    'raw_score': 7.0 if abs(growth_change) > threshold * 2 else 6.0
                })
            
            # Check for unusual volatility
            if std_growth > abs(avg_growth) * 2:
                insights.append({
                    'type': 'high_volatility',
                    'category': 'time_series',
                    'title': f"High volatility in {metric} growth",
                    'data': {
                        'metric': metric,
                        'avg_growth': float(avg_growth),
                        'std_deviation': float(std_growth),
                        'coefficient_of_variation': float((std_growth / abs(avg_growth)) * 100) if avg_growth != 0 else 0
                    },
                    'raw_score': 6.5
                })
        
        except Exception as e:
            print(f"Error in growth rate analysis for {metric}: {e}")
        
        return insights
    
    def _detect_volatility(self, time_col: str, metric: str, granularity: str) -> List[Dict[str, Any]]:
        """Detect periods of unusual volatility."""
        insights = []
        
        try:
            ts_data = self.engine.get_time_series_aggregation(
                time_col, metric, 'AVG', granularity
            )
            
            if len(ts_data) < 10:
                return []
            
            df = ts_data.to_pandas()
            values = df['value'].dropna().values
            
            if len(values) < 10:
                return []
            
            # Calculate rolling std deviation
            window_size = min(5, len(values) // 3)
            rolling_std = np.array([np.std(values[max(0, i-window_size):i+1]) 
                                   for i in range(len(values))])
            
            # Detect sudden volatility spikes
            avg_std = np.mean(rolling_std[window_size:])
            std_of_std = np.std(rolling_std[window_size:])
            
            volatility_threshold = avg_std + 2 * std_of_std
            
            spike_indices = np.where(rolling_std > volatility_threshold)[0]
            
            if len(spike_indices) > 0:
                insights.append({
                    'type': 'volatility_spike',
                    'category': 'time_series',
                    'title': f"Volatility spikes detected in {metric}",
                    'data': {
                        'metric': metric,
                        'num_spikes': int(len(spike_indices)),
                        'avg_volatility': float(avg_std),
                        'peak_volatility': float(np.max(rolling_std))
                    },
                    'raw_score': 6.0
                })
        
        except Exception as e:
            print(f"Error in volatility detection for {metric}: {e}")
        
        return insights
    
    def _create_trend_chart(self, df, metric: str, slope: float, intercept: float):
        """Create time series chart with trend line."""
        try:
            fig = go.Figure()
            
            # Actual values
            fig.add_trace(go.Scatter(
                x=df['period'],
                y=df['value'],
                mode='lines+markers',
                name='Actual',
                line=dict(color='blue', width=2)
            ))
            
            # Trend line
            x_numeric = np.arange(len(df))
            trend_line = slope * x_numeric + intercept
            
            fig.add_trace(go.Scatter(
                x=df['period'],
                y=trend_line,
                mode='lines',
                name='Trend',
                line=dict(color='red', width=2, dash='dash')
            ))
            
            fig.update_layout(
                title=f"{metric} over time with trend",
                xaxis_title="Period",
                yaxis_title=metric,
                template="plotly_white",
                height=400,
                showlegend=True
            )
            
            return fig
        except:
            return None
