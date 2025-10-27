"""Anomaly Detector - Outlier detection using multiple methods"""
from typing import List, Dict, Any
from core.duckdb_engine import DuckDBEngine
import numpy as np
import plotly.graph_objects as go
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self, parquet_path: str, config: Dict[str, Any]):
        self.engine = DuckDBEngine(parquet_path)
        self.config = config
        self.outlier_threshold = config.get('outlier_threshold', 3.0)
    
    def detect(self) -> List[Dict[str, Any]]:
        """Detect anomalies using multiple methods."""
        insights = []
        
        metrics = self.config.get('key_metrics', [])
        
        for metric in metrics:
            insights.extend(self._detect_outliers_zscore(metric))
            insights.extend(self._detect_outliers_iqr(metric))
        
        # Multivariate anomaly detection if multiple metrics
        if len(metrics) >= 2:
            insights.extend(self._detect_multivariate_anomalies(metrics))
        
        return insights
    
    def _detect_outliers_zscore(self, metric: str) -> List[Dict[str, Any]]:
        """Detect outliers using Z-score method."""
        insights = []
        
        try:
            # Get statistics
            stats = self.engine.get_numeric_stats(metric)
            mean = stats.get('mean', 0)
            std = stats.get('std', 0)
            
            if std == 0:
                return []
            
            # Find outliers
            lower_bound = mean - self.outlier_threshold * std
            upper_bound = mean + self.outlier_threshold * std
            
            outliers = self.engine.query(f"""
                SELECT 
                    {metric},
                    ({metric} - {mean}) / {std} as z_score
                FROM data
                WHERE {metric} IS NOT NULL
                    AND ({metric} < {lower_bound} OR {metric} > {upper_bound})
                LIMIT 100
            """)
            
            if len(outliers) == 0:
                return []
            
            df = outliers.to_pandas()
            num_outliers = len(df)
            
            # Get total count
            total_count = self.engine.query(f"""
                SELECT COUNT(*) as total FROM data WHERE {metric} IS NOT NULL
            """).to_pandas().iloc[0]['total']
            
            outlier_pct = (num_outliers / total_count) * 100 if total_count > 0 else 0
            
            # Only report if significant
            if outlier_pct > 0.5:  # More than 0.5% are outliers
                # Get extreme values
                max_outlier = df.nlargest(1, 'z_score').iloc[0] if len(df) > 0 else None
                min_outlier = df.nsmallest(1, 'z_score').iloc[0] if len(df) > 0 else None
                
                # Create box plot
                chart = self._create_outlier_chart(metric)
                
                score = 6.0 + min(outlier_pct / 2, 2)
                
                insights.append({
                    'type': 'outliers_zscore',
                    'category': 'anomaly',
                    'title': f"Outliers detected in {metric} (Z-score method)",
                    'data': {
                        'metric': metric,
                        'method': 'Z-score',
                        'threshold': float(self.outlier_threshold),
                        'num_outliers': int(num_outliers),
                        'outlier_percentage': float(outlier_pct),
                        'mean': float(mean),
                        'std': float(std),
                        'max_z_score': float(max_outlier['z_score']) if max_outlier is not None else 0,
                        'min_z_score': float(min_outlier['z_score']) if min_outlier is not None else 0
                    },
                    'chart': chart,
                    'raw_score': score
                })
        
        except Exception as e:
            print(f"Error in Z-score outlier detection for {metric}: {e}")
        
        return insights
    
    def _detect_outliers_iqr(self, metric: str) -> List[Dict[str, Any]]:
        """Detect outliers using IQR method."""
        insights = []
        
        try:
            # Get quartiles
            stats = self.engine.get_numeric_stats(metric)
            q25 = stats.get('q25', 0)
            q75 = stats.get('q75', 0)
            iqr = q75 - q25
            
            if iqr == 0:
                return []
            
            # Calculate bounds
            multiplier = 1.5
            lower_bound = q25 - multiplier * iqr
            upper_bound = q75 + multiplier * iqr
            
            # Find outliers
            outliers = self.engine.query(f"""
                SELECT {metric}
                FROM data
                WHERE {metric} IS NOT NULL
                    AND ({metric} < {lower_bound} OR {metric} > {upper_bound})
            """)
            
            if len(outliers) == 0:
                return []
            
            num_outliers = len(outliers)
            
            # Get total count
            total_count = self.engine.query(f"""
                SELECT COUNT(*) as total FROM data WHERE {metric} IS NOT NULL
            """).to_pandas().iloc[0]['total']
            
            outlier_pct = (num_outliers / total_count) * 100 if total_count > 0 else 0
            
            # Only report if significant and different from Z-score
            if outlier_pct > 1.0:  # More than 1% are outliers
                score = 5.5 + min(outlier_pct / 3, 2)
                
                insights.append({
                    'type': 'outliers_iqr',
                    'category': 'anomaly',
                    'title': f"Outliers detected in {metric} (IQR method)",
                    'data': {
                        'metric': metric,
                        'method': 'IQR',
                        'multiplier': multiplier,
                        'num_outliers': int(num_outliers),
                        'outlier_percentage': float(outlier_pct),
                        'q25': float(q25),
                        'q75': float(q75),
                        'iqr': float(iqr),
                        'lower_bound': float(lower_bound),
                        'upper_bound': float(upper_bound)
                    },
                    'raw_score': score
                })
        
        except Exception as e:
            print(f"Error in IQR outlier detection for {metric}: {e}")
        
        return insights
    
    def _detect_multivariate_anomalies(self, metrics: List[str]) -> List[Dict[str, Any]]:
        """Detect anomalies using multivariate analysis."""
        insights = []
        
        try:
            # Get data for all metrics
            metrics_str = ', '.join(metrics)
            data = self.engine.query(f"""
                SELECT {metrics_str}
                FROM data
                WHERE {' AND '.join([f'{m} IS NOT NULL' for m in metrics])}
                LIMIT 10000
            """)
            
            if len(data) < 100:
                return []
            
            # Convert to numpy
            X = data.to_numpy()
            
            # Use Isolation Forest
            clf = IsolationForest(contamination=0.05, random_state=42)
            predictions = clf.fit_predict(X)
            
            # Count anomalies
            num_anomalies = np.sum(predictions == -1)
            anomaly_pct = (num_anomalies / len(predictions)) * 100
            
            if num_anomalies > 0:
                score = 6.5 + min(anomaly_pct / 10, 2)
                
                insights.append({
                    'type': 'multivariate_anomalies',
                    'category': 'anomaly',
                    'title': f"Multivariate anomalies detected across {len(metrics)} metrics",
                    'data': {
                        'metrics': metrics,
                        'method': 'Isolation Forest',
                        'num_anomalies': int(num_anomalies),
                        'anomaly_percentage': float(anomaly_pct),
                        'interpretation': 'Records with unusual combinations of metric values'
                    },
                    'raw_score': score
                })
        
        except Exception as e:
            print(f"Error in multivariate anomaly detection: {e}")
        
        return insights
    
    def _create_outlier_chart(self, metric: str):
        """Create box plot for outlier visualization."""
        try:
            # Get sample data
            data = self.engine.query(f"""
                SELECT {metric}
                FROM data
                WHERE {metric} IS NOT NULL
                LIMIT 5000
            """).to_numpy().flatten()
            
            fig = go.Figure()
            
            fig.add_trace(go.Box(
                y=data,
                name=metric,
                boxmean='sd'
            ))
            
            fig.update_layout(
                title=f"Distribution of {metric} with outliers",
                yaxis_title=metric,
                template="plotly_white",
                height=400,
                showlegend=False
            )
            
            return fig
        except:
            return None
