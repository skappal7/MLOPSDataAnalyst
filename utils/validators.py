"""Validation Functions"""

def validate_dataframe(df):
    """Validate DataFrame requirements."""
    if df is None or len(df) == 0:
        raise ValueError("DataFrame is empty")
    return True
