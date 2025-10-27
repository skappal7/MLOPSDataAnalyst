"""
Data Profiler
=============
Automated profiling and schema detection.
"""

import polars as pl
from typing import Dict, Any
from core.duckdb_engine import DuckDBEngine


class DataProfiler:
    """Generate comprehensive data profile."""
    
    @staticmethod
    def generate_profile(parquet_path: str) -> Dict[str, Any]:
        """
        Generate complete data profile.
        
        Args:
            parquet_path: Path to Parquet file
            
        Returns:
            Profile dictionary
        """
        # Load with Polars for schema
        df = pl.read_parquet(parquet_path)
        
        # Initialize DuckDB engine
        engine = DuckDBEngine(parquet_path)
        
        profile = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'numeric_columns': [],
            'categorical_columns': [],
            'date_columns': [],
            'text_columns': [],
            'boolean_columns': [],
            'column_stats': {},
            'memory_usage_mb': df.estimated_size() / (1024 * 1024)
        }
        
        # Analyze each column
        for col in df.columns:
            dtype = df[col].dtype
            n_unique = df[col].n_unique()
            
            if dtype in [pl.Int8, pl.Int16, pl.Int32, pl.Int64, 
                        pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
                        pl.Float32, pl.Float64]:
                # Numeric column - check if actually categorical
                if n_unique > 10 and n_unique > len(df) * 0.05:
                    profile['numeric_columns'].append(col)
                else:
                    profile['categorical_columns'].append(col)
            
            elif dtype in [pl.Utf8, pl.Categorical]:
                if n_unique <= 50:
                    profile['categorical_columns'].append(col)
                else:
                    profile['text_columns'].append(col)
            
            elif dtype in [pl.Date, pl.Datetime]:
                profile['date_columns'].append(col)
            
            elif dtype == pl.Boolean:
                profile['boolean_columns'].append(col)
                profile['categorical_columns'].append(col)  # Also treat as categorical
        
        engine.close()
        return profile
