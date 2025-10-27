"""Helper Functions"""
from typing import Any

def format_bytes(size_bytes: int) -> str:
    """Format bytes to human-readable."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def format_number(num: Any) -> str:
    """Format large numbers with commas."""
    try:
        return f"{int(num):,}"
    except:
        return str(num)
