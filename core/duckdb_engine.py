"""
DuckDB Engine
============
High-performance SQL analytics on Parquet files.
"""

import duckdb
from typing import Dict, List, Any, Optional
import polars as pl
import streamlit as st


class DuckDBEngine:
    """
    DuckDB-based analytics engine.
    
    Provides:
    - Fast SQL queries on Parquet
    - Aggregations and window functions
    - Statistical calculations
    - Time-series operations
    """
    
    def __init__(self, parquet_path: str):
        """
        Initialize DuckDB connection.
        
        Args:
            parquet_path: Path to Parquet file
        """
        self.parquet_path = parquet_path
        self.con = duckdb.connect(':memory:')  # In-memory database
        
        # Register Parquet file as table
        self.con.execute(f"""
            CREATE VIEW data AS 
            SELECT * FROM read_parquet('{parquet_path}')
        """)
    
    def query(self, sql: str) -> pl.DataFrame:
        """
        Execute SQL query and return Polars DataFrame.
        
        Args:
            sql: SQL query string
            
        Returns:
            Polars DataFrame with results
        """
        result = self.con.execute(sql).pl()
        return result
    
    def get_column_summary(self, column: str) -> Dict[str, Any]:
        """
        Get comprehensive summary for a column.
        
        Args:
            column: Column name
            
        Returns:
            Dictionary with summary statistics
        """
        sql = f"""
            SELECT 
                COUNT(*) as total_count,
                COUNT({column}) as non_null_count,
                COUNT(DISTINCT {column}) as unique_count,
                MIN({column}) as min_value,
                MAX({column}) as max_value
            FROM data
        """
        
        result = self.query(sql).to_dicts()[0]
        return result
    
    def get_numeric_stats(self, column: str) -> Dict[str, float]:
        """
        Get statistical summary for numeric column.
        
        Args:
            column: Numeric column name
            
        Returns:
            Dictionary with mean, median, std, etc.
        """
        sql = f"""
            SELECT 
                AVG({column}) as mean,
                MEDIAN({column}) as median,
                STDDEV({column}) as std,
                MIN({column}) as min,
                QUANTILE({column}, 0.25) as q25,
                QUANTILE({column}, 0.50) as q50,
                QUANTILE({column}, 0.75) as q75,
                MAX({column}) as max,
                VARIANCE({column}) as variance,
                SKEWNESS({column}) as skewness,
                KURTOSIS({column}) as kurtosis
            FROM data
            WHERE {column} IS NOT NULL
        """
        
        result = self.query(sql).to_dicts()[0]
        return result
    
    def get_categorical_distribution(self, column: str, top_n: int = 20) -> pl.DataFrame:
        """
        Get value distribution for categorical column.
        
        Args:
            column: Categorical column name
            top_n: Number of top categories to return
            
        Returns:
            DataFrame with counts and percentages
        """
        sql = f"""
            SELECT 
                {column} as category,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
            FROM data
            WHERE {column} IS NOT NULL
            GROUP BY {column}
            ORDER BY count DESC
            LIMIT {top_n}
        """
        
        return self.query(sql)
    
    def get_correlation_matrix(self, numeric_columns: List[str]) -> pl.DataFrame:
        """
        Calculate correlation matrix for numeric columns.
        
        Args:
            numeric_columns: List of numeric column names
            
        Returns:
            Correlation matrix as DataFrame
        """
        if len(numeric_columns) < 2:
            return pl.DataFrame()
        
        # Build correlation query
        correlations = []
        for i, col1 in enumerate(numeric_columns):
            for col2 in numeric_columns[i:]:
                sql = f"""
                    SELECT 
                        '{col1}' as var1,
                        '{col2}' as var2,
                        CORR({col1}, {col2}) as correlation
                    FROM data
                    WHERE {col1} IS NOT NULL AND {col2} IS NOT NULL
                """
                corr_result = self.query(sql)
                correlations.append(corr_result)
        
        # Combine results
        if correlations:
            return pl.concat(correlations)
        return pl.DataFrame()
    
    def get_time_series_aggregation(
        self, 
        date_column: str, 
        metric_column: str, 
        agg_func: str = 'SUM',
        granularity: str = 'day'
    ) -> pl.DataFrame:
        """
        Aggregate time series data.
        
        Args:
            date_column: Date/datetime column
            metric_column: Metric to aggregate
            agg_func: Aggregation function (SUM, AVG, COUNT, etc.)
            granularity: Time granularity (day, week, month, quarter, year)
            
        Returns:
            Aggregated time series DataFrame
        """
        # Map granularity to DuckDB date_trunc
        trunc_map = {
            'day': 'day',
            'week': 'week',
            'month': 'month',
            'quarter': 'quarter',
            'year': 'year'
        }
        
        trunc_level = trunc_map.get(granularity, 'day')
        
        sql = f"""
            SELECT 
                DATE_TRUNC('{trunc_level}', {date_column}) as period,
                {agg_func}({metric_column}) as value
            FROM data
            WHERE {date_column} IS NOT NULL 
                AND {metric_column} IS NOT NULL
            GROUP BY period
            ORDER BY period
        """
        
        return self.query(sql)
    
    def get_segment_comparison(
        self, 
        segment_column: str, 
        metric_column: str,
        agg_func: str = 'AVG'
    ) -> pl.DataFrame:
        """
        Compare metric across segments.
        
        Args:
            segment_column: Categorical column for segments
            metric_column: Metric to compare
            agg_func: Aggregation function
            
        Returns:
            DataFrame with segment comparisons
        """
        sql = f"""
            SELECT 
                {segment_column} as segment,
                COUNT(*) as count,
                {agg_func}({metric_column}) as metric_value,
                STDDEV({metric_column}) as std_dev,
                MIN({metric_column}) as min_value,
                MAX({metric_column}) as max_value
            FROM data
            WHERE {segment_column} IS NOT NULL 
                AND {metric_column} IS NOT NULL
            GROUP BY {segment_column}
            ORDER BY metric_value DESC
        """
        
        return self.query(sql)
    
    def get_period_over_period(
        self,
        date_column: str,
        metric_column: str,
        periods: List[str]  # e.g., ['2024-01', '2024-02']
    ) -> pl.DataFrame:
        """
        Compare metrics between periods.
        
        Args:
            date_column: Date column
            metric_column: Metric to compare
            periods: List of period strings
            
        Returns:
            DataFrame with period comparison
        """
        period_filters = " OR ".join([
            f"DATE_TRUNC('month', {date_column}) = '{period}'"
            for period in periods
        ])
        
        sql = f"""
            SELECT 
                DATE_TRUNC('month', {date_column}) as period,
                SUM({metric_column}) as total,
                AVG({metric_column}) as average,
                COUNT(*) as count
            FROM data
            WHERE {period_filters}
            GROUP BY period
            ORDER BY period
        """
        
        return self.query(sql)
    
    def detect_outliers_iqr(
        self, 
        column: str, 
        multiplier: float = 1.5
    ) -> pl.DataFrame:
        """
        Detect outliers using IQR method.
        
        Args:
            column: Numeric column
            multiplier: IQR multiplier (default 1.5)
            
        Returns:
            DataFrame with outliers
        """
        sql = f"""
            WITH stats AS (
                SELECT 
                    QUANTILE({column}, 0.25) as q25,
                    QUANTILE({column}, 0.75) as q75,
                    QUANTILE({column}, 0.75) - QUANTILE({column}, 0.25) as iqr
                FROM data
                WHERE {column} IS NOT NULL
            )
            SELECT *
            FROM data, stats
            WHERE {column} < (q25 - {multiplier} * iqr)
                OR {column} > (q75 + {multiplier} * iqr)
        """
        
        return self.query(sql)
    
    def get_top_bottom_n(
        self,
        column: str,
        n: int = 10,
        order: str = 'DESC'
    ) -> pl.DataFrame:
        """
        Get top or bottom N records by column.
        
        Args:
            column: Column to sort by
            n: Number of records
            order: 'DESC' for top, 'ASC' for bottom
            
        Returns:
            DataFrame with top/bottom records
        """
        sql = f"""
            SELECT *
            FROM data
            WHERE {column} IS NOT NULL
            ORDER BY {column} {order}
            LIMIT {n}
        """
        
        return self.query(sql)
    
    def calculate_growth_rate(
        self,
        date_column: str,
        metric_column: str,
        granularity: str = 'month'
    ) -> pl.DataFrame:
        """
        Calculate period-over-period growth rates.
        
        Args:
            date_column: Date column
            metric_column: Metric column
            granularity: Time granularity
            
        Returns:
            DataFrame with growth rates
        """
        trunc_map = {'day': 'day', 'week': 'week', 'month': 'month', 'year': 'year'}
        trunc_level = trunc_map.get(granularity, 'month')
        
        sql = f"""
            WITH aggregated AS (
                SELECT 
                    DATE_TRUNC('{trunc_level}', {date_column}) as period,
                    SUM({metric_column}) as value
                FROM data
                WHERE {date_column} IS NOT NULL 
                    AND {metric_column} IS NOT NULL
                GROUP BY period
            ),
            with_lag AS (
                SELECT 
                    period,
                    value,
                    LAG(value, 1) OVER (ORDER BY period) as prev_value
                FROM aggregated
            )
            SELECT 
                period,
                value,
                prev_value,
                ROUND((value - prev_value) / NULLIF(prev_value, 0) * 100, 2) as growth_rate_pct
            FROM with_lag
            WHERE prev_value IS NOT NULL
            ORDER BY period
        """
        
        return self.query(sql)
    
    def close(self):
        """Close DuckDB connection."""
        if self.con:
            self.con.close()
