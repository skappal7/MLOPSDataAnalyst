"""
Data Processor
=============
Handles data ingestion, Parquet conversion, and schema detection using Polars.
"""

import polars as pl
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
import streamlit as st


class DataProcessor:
    """
    Fast data processing with Polars.
    
    Handles:
    - CSV/Excel ingestion
    - Parquet conversion
    - Schema detection
    - Data preview
    """
    
    def __init__(self):
        self.df: Optional[pl.DataFrame] = None
        self.parquet_path: Optional[str] = None
        self.schema: Optional[Dict[str, Any]] = None
    
    @st.cache_data(show_spinner=False)
    def load_file(_self, uploaded_file) -> str:
        """
        Load file and convert to Parquet.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            str: Path to generated Parquet file
        """
        file_extension = Path(uploaded_file.name).suffix.lower()
        
        try:
            # Step 1: Load with Polars
            if file_extension == '.csv':
                _self.df = pl.read_csv(
                    uploaded_file,
                    infer_schema_length=10000,  # Sample rows for type inference
                    try_parse_dates=True,
                    null_values=['', 'NULL', 'null', 'NA', 'N/A', 'n/a']
                )
            
            elif file_extension in ['.xlsx', '.xls']:
                _self.df = pl.read_excel(
                    uploaded_file,
                    infer_schema_length=10000
                )
            
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            # Step 2: Convert to Parquet
            temp_dir = tempfile.gettempdir()
            parquet_filename = f"data_{hash(uploaded_file.name)}.parquet"
            _self.parquet_path = str(Path(temp_dir) / parquet_filename)
            
            _self.df.write_parquet(
                _self.parquet_path,
                compression='zstd',  # Best compression/speed balance
                statistics=True  # Enable column statistics for faster queries
            )
            
            # Step 3: Extract schema
            _self._extract_schema()
            
            return _self.parquet_path
            
        except Exception as e:
            raise Exception(f"Error loading file: {str(e)}")
    
    def _extract_schema(self):
        """Extract schema information from dataframe."""
        if self.df is None:
            return
        
        schema = {
            'columns': [],
            'numeric_columns': [],
            'categorical_columns': [],
            'date_columns': [],
            'boolean_columns': [],
            'text_columns': [],
            'dtypes': {}
        }
        
        for col in self.df.columns:
            dtype = self.df[col].dtype
            dtype_str = str(dtype)
            
            schema['columns'].append(col)
            schema['dtypes'][col] = dtype_str
            
            # Categorize by type
            if dtype in [pl.Int8, pl.Int16, pl.Int32, pl.Int64, 
                        pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
                        pl.Float32, pl.Float64]:
                # Check if it's actually categorical (low cardinality)
                n_unique = self.df[col].n_unique()
                if n_unique <= 50 and n_unique < len(self.df) * 0.05:
                    schema['categorical_columns'].append(col)
                else:
                    schema['numeric_columns'].append(col)
            
            elif dtype in [pl.Utf8, pl.Categorical]:
                n_unique = self.df[col].n_unique()
                if n_unique <= 100:  # Likely categorical
                    schema['categorical_columns'].append(col)
                else:
                    schema['text_columns'].append(col)
            
            elif dtype in [pl.Date, pl.Datetime]:
                schema['date_columns'].append(col)
            
            elif dtype == pl.Boolean:
                schema['boolean_columns'].append(col)
        
        self.schema = schema
    
    def get_schema(self) -> Dict[str, Any]:
        """Get schema information."""
        return self.schema
    
    def get_preview(self, n_rows: int = 100) -> pl.DataFrame:
        """
        Get preview of data.
        
        Args:
            n_rows: Number of rows to return
            
        Returns:
            Polars DataFrame with preview
        """
        if self.df is None:
            return pl.DataFrame()
        
        return self.df.head(n_rows)
    
    def get_column_stats(self, column: str) -> Dict[str, Any]:
        """
        Get basic statistics for a column.
        
        Args:
            column: Column name
            
        Returns:
            Dictionary with statistics
        """
        if self.df is None or column not in self.df.columns:
            return {}
        
        col_data = self.df[column]
        dtype = col_data.dtype
        
        stats = {
            'name': column,
            'dtype': str(dtype),
            'null_count': col_data.null_count(),
            'null_percentage': col_data.null_count() / len(col_data) * 100,
            'unique_count': col_data.n_unique(),
        }
        
        # Numeric statistics
        if dtype in [pl.Int8, pl.Int16, pl.Int32, pl.Int64, 
                     pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
                     pl.Float32, pl.Float64]:
            stats.update({
                'mean': col_data.mean(),
                'median': col_data.median(),
                'std': col_data.std(),
                'min': col_data.min(),
                'max': col_data.max(),
                'q25': col_data.quantile(0.25),
                'q75': col_data.quantile(0.75),
            })
        
        # Categorical statistics
        elif dtype in [pl.Utf8, pl.Categorical]:
            value_counts = col_data.value_counts().head(10)
            stats['top_values'] = value_counts.to_dicts()
        
        return stats
    
    def get_parquet_path(self) -> Optional[str]:
        """Get path to Parquet file."""
        return self.parquet_path
    
    def get_dataframe(self) -> Optional[pl.DataFrame]:
        """Get the Polars DataFrame."""
        return self.df
    
    @staticmethod
    def load_parquet(path: str) -> pl.DataFrame:
        """
        Load Parquet file directly.
        
        Args:
            path: Path to Parquet file
            
        Returns:
            Polars DataFrame
        """
        return pl.read_parquet(path)
    
    def optimize_dtypes(self):
        """
        Optimize column data types for memory efficiency.
        
        Converts:
        - String columns with low cardinality to Categorical
        - Large integers to smaller types if possible
        """
        if self.df is None:
            return
        
        optimized = self.df
        
        for col in optimized.columns:
            dtype = optimized[col].dtype
            
            # Convert low-cardinality strings to categorical
            if dtype == pl.Utf8:
                n_unique = optimized[col].n_unique()
                if n_unique <= 50 and n_unique < len(optimized) * 0.5:
                    optimized = optimized.with_columns(
                        pl.col(col).cast(pl.Categorical)
                    )
            
            # Downcast integers (safely)
            elif dtype in [pl.Int64, pl.UInt64]:
                col_min = optimized[col].min()
                col_max = optimized[col].max()
                
                if col_min >= 0:  # Unsigned
                    if col_max < 256:
                        optimized = optimized.with_columns(
                            pl.col(col).cast(pl.UInt8)
                        )
                    elif col_max < 65536:
                        optimized = optimized.with_columns(
                            pl.col(col).cast(pl.UInt16)
                        )
                else:  # Signed
                    if col_min >= -128 and col_max < 128:
                        optimized = optimized.with_columns(
                            pl.col(col).cast(pl.Int8)
                        )
                    elif col_min >= -32768 and col_max < 32768:
                        optimized = optimized.with_columns(
                            pl.col(col).cast(pl.Int16)
                        )
        
        self.df = optimized
        
        # Re-extract schema after optimization
        self._extract_schema()
