"""
Analysis Configuration
=====================
Default thresholds and parameters for statistical analysis.
"""

# ============================================================================
# STATISTICAL THRESHOLDS
# ============================================================================

STATISTICAL_CONFIG = {
    # Significance levels
    'p_value_threshold': 0.05,  # Standard 95% confidence
    'correlation_threshold': 0.6,  # Strong correlation minimum
    
    # Outlier detection
    'outlier_z_score': 3.0,  # Standard deviations for outliers
    'outlier_iqr_multiplier': 1.5,  # IQR method multiplier
    
    # Change detection
    'change_threshold_pct': 0.15,  # 15% change is notable
    'trend_window': 7,  # Days for trend calculation
    
    # Time series
    'seasonality_threshold': 0.3,  # Minimum seasonal strength
    'trend_significance': 0.05,  # P-value for trend tests
    
    # Clustering
    'min_cluster_size': 20,  # Minimum records per cluster
    'max_clusters': 8,  # Maximum number of clusters
    
    # Categorical analysis
    'chi_square_threshold': 0.05,  # P-value for independence tests
    'min_category_frequency': 5,  # Minimum occurrences
}


# ============================================================================
# INSIGHT SCORING WEIGHTS
# ============================================================================

SCORING_WEIGHTS = {
    'statistical_significance': 3.0,  # High weight for p-values
    'magnitude': 2.5,  # Size of effect/change
    'rarity': 2.0,  # How unusual the pattern is
    'business_impact': 2.0,  # Affects key metrics
    'actionability': 1.5,  # Clear next steps available
    'novelty': 1.0,  # Non-obvious finding
}


# ============================================================================
# DATA PROFILING
# ============================================================================

PROFILING_CONFIG = {
    'sample_size_for_inference': 10000,  # Rows to infer types
    'max_unique_for_categorical': 50,  # Max unique values for categorical
    'min_numeric_unique': 10,  # Min unique for numeric (not ID)
    'date_formats': [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y/%m/%d',
        '%Y-%m-%d %H:%M:%S'
    ],
}


# ============================================================================
# EXPORT SETTINGS
# ============================================================================

EXPORT_CONFIG = {
    'pdf': {
        'page_size': 'A4',
        'margin': '2cm',
        'font_family': 'Arial',
        'title_size': '24px',
        'body_size': '11px',
    },
    'excel': {
        'freeze_panes': True,
        'auto_filter': True,
        'column_width': 15,
        'wrap_text': True,
    },
    'markdown': {
        'include_toc': True,
        'max_heading_level': 3,
    }
}


# ============================================================================
# DOMAIN-SPECIFIC RULES
# ============================================================================

DOMAIN_RULES = {
    'sales': {
        'expected_seasonality': 'Q4_peak',
        'key_metrics': ['revenue', 'units', 'profit', 'orders'],
        'important_dimensions': ['region', 'category', 'customer_type'],
        'alert_metrics': ['revenue', 'profit_margin'],
    },
    'marketing': {
        'expected_seasonality': 'campaign_driven',
        'key_metrics': ['impressions', 'clicks', 'conversions', 'ctr', 'cpc'],
        'important_dimensions': ['channel', 'campaign', 'audience'],
        'alert_metrics': ['ctr', 'conversion_rate', 'roas'],
    },
    'operations': {
        'expected_seasonality': 'weekday_pattern',
        'key_metrics': ['volume', 'throughput', 'efficiency', 'defect_rate'],
        'important_dimensions': ['location', 'shift', 'line'],
        'alert_metrics': ['defect_rate', 'downtime'],
    },
    'customer': {
        'expected_seasonality': 'lifecycle_driven',
        'key_metrics': ['ltv', 'churn_rate', 'engagement', 'satisfaction'],
        'important_dimensions': ['segment', 'cohort', 'tenure'],
        'alert_metrics': ['churn_rate', 'nps'],
    },
}


# ============================================================================
# NARRATIVE TEMPLATES
# ============================================================================

def get_domain_context(domain):
    """Get domain-specific configuration."""
    return DOMAIN_RULES.get(domain, DOMAIN_RULES['sales'])  # Default to sales


def get_alert_threshold(metric_type='default'):
    """Get appropriate threshold for metric type."""
    thresholds = {
        'percentage': 0.10,  # 10% change
        'currency': 0.15,  # 15% change
        'count': 0.20,  # 20% change
        'rate': 0.05,  # 5% change (rates are sensitive)
        'default': 0.15,  # 15% default
    }
    return thresholds.get(metric_type, thresholds['default'])
