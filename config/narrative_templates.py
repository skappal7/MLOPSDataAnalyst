"""
Narrative Templates
==================
Template strings for generating human-readable insight narratives.
"""

# ============================================================================
# STATISTICAL INSIGHTS
# ============================================================================

CORRELATION_TEMPLATES = {
    'strong_positive': """
**Strong Positive Correlation Detected**

{var1} and {var2} show a strong positive relationship (r = {correlation:.2f}, p < {p_value:.3f}).

This means:
- When {var1} increases, {var2} tends to increase proportionally
- Statistical confidence: {confidence}%
- {context_statement}

**Implication:** {implication}
""",
    
    'strong_negative': """
**Strong Negative Correlation Detected**

{var1} and {var2} show a strong negative relationship (r = {correlation:.2f}, p < {p_value:.3f}).

This means:
- When {var1} increases, {var2} tends to decrease
- Statistical confidence: {confidence}%
- {context_statement}

**Implication:** {implication}
""",
    
    'unexpected': """
**Unexpected Relationship**

{var1} and {var2} correlation: {correlation:.2f} (p < {p_value:.3f})

This is unusual because {reason}.

Historical pattern: {historical_context}

**Action Required:** {recommendation}
"""
}


# ============================================================================
# TIME SERIES INSIGHTS
# ============================================================================

TIME_SERIES_TEMPLATES = {
    'trend_change': """
**Trend Reversal Detected**

{metric} showed a significant trend change in {period}:
- Previous trend: {previous_trend} ({previous_rate:+.1f}% per {unit})
- New trend: {new_trend} ({new_rate:+.1f}% per {unit})
- Change point: {change_date}
- Statistical significance: p < {p_value:.3f}

{context_explanation}

**Impact:** {impact_statement}
""",
    
    'seasonality': """
**Seasonal Pattern Identified**

{metric} exhibits {strength} seasonality:
- Cycle: {cycle_type} ({period} {unit})
- Peak periods: {peak_description}
- Trough periods: {trough_description}
- Amplitude: ±{amplitude:.1f}%

{business_context}

**Planning Insight:** {recommendation}
""",
    
    'anomaly_period': """
**Anomalous Period Detected**

{metric} in {period}: {value} ({deviation:+.1%} vs expected {expected})

Context:
- This exceeds {threshold:.0f}× the typical variation
- Historical range: {min_val} to {max_val}
- Z-score: {z_score:.2f}

{investigation_prompt}
"""
}


# ============================================================================
# CATEGORICAL INSIGHTS
# ============================================================================

CATEGORICAL_TEMPLATES = {
    'segment_divergence': """
**Significant Segment Divergence**

{dimension} shows divergent performance on {metric}:

Top performers:
{top_segments}

Underperformers:
{bottom_segments}

Statistical test: χ² = {chi_square:.2f}, p < {p_value:.3f}

{context_statement}

**Recommendation:** {action}
""",
    
    'category_shift': """
**Category Distribution Shift**

{dimension} distribution changed significantly {comparison_period}:

Changes:
{changes_table}

Overall shift: {shift_type} (p < {p_value:.3f})

{business_impact}
""",
    
    'concentration': """
**High Concentration Detected**

{dimension}: Top {n} categories account for {percentage:.1f}% of {metric}

Distribution:
{distribution_summary}

{risk_or_opportunity}
"""
}


# ============================================================================
# ANOMALY INSIGHTS
# ============================================================================

ANOMALY_TEMPLATES = {
    'outliers': """
**Outliers Detected**

Found {count} outlier(s) in {metric}:
- Method: {detection_method}
- Threshold: {threshold} ({threshold_type})
- Date/Period: {when}

Examples:
{outlier_examples}

{pattern_description}

**Action:** {recommendation}
""",
    
    'cluster_anomaly': """
**Unusual Cluster Identified**

Cluster #{cluster_id} ({size} records, {percentage:.1f}% of data) shows distinct pattern:

Characteristics:
{characteristics}

This cluster is unusual because:
{reason}

**Investigation:** {next_steps}
""",
    
    'rare_combination': """
**Rare Combination Detected**

Unusual pattern: {combination_description}
- Frequency: {count} occurrences ({percentage:.2f}%)
- Expected frequency: {expected} ({expected_percentage:.2f}%)
- Rarity score: {rarity_score:.1f}/10

{context}
"""
}


# ============================================================================
# COMPARISON INSIGHTS
# ============================================================================

COMPARISON_TEMPLATES = {
    'period_over_period': """
**{comparison_type} Change**

{metric}: {current_value} ({period_current}) vs {previous_value} ({period_previous})
- Change: {absolute_change} ({percentage_change:+.1%})
- Threshold: ±{threshold:.1%}
- Status: {status_icon} {status_text}

Context:
{context_statement}

{additional_analysis}
""",
    
    'vs_target': """
**Target Performance**

{metric}: {actual_value} vs target {target_value}
- Gap: {gap} ({gap_percentage:+.1%})
- Status: {status}

Trajectory:
{trend_statement}

{forecast_statement}
""",
    
    'benchmark': """
**Benchmark Comparison**

{metric}: Your value is {position} in the distribution
- Your value: {your_value}
- Benchmark median: {benchmark_median}
- Percentile: {percentile}th

{context}
"""
}


# ============================================================================
# ML INSIGHTS
# ============================================================================

ML_TEMPLATES = {
    'clustering': """
**Clustering Analysis**

Identified {n_clusters} distinct segments in the data:

{cluster_descriptions}

Key differentiators:
{differentiators}

**Application:** {use_case}
""",
    
    'pca': """
**Dimensionality Analysis**

Principal components explain {variance_explained:.1f}% of variation:
{components_summary}

Key insights:
{insights}
""",
    
    'prediction': """
**Forecast**

{metric} projection for {period}:
- Predicted value: {forecast_value}
- Confidence interval: [{lower_bound}, {upper_bound}]
- Model: {model_type} (R² = {r_squared:.3f})

{trend_statement}
"""
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_template(category, template_type):
    """Retrieve template by category and type."""
    templates = {
        'correlation': CORRELATION_TEMPLATES,
        'time_series': TIME_SERIES_TEMPLATES,
        'categorical': CATEGORICAL_TEMPLATES,
        'anomaly': ANOMALY_TEMPLATES,
        'comparison': COMPARISON_TEMPLATES,
        'ml': ML_TEMPLATES,
    }
    return templates.get(category, {}).get(template_type, "")


def format_template(template, **kwargs):
    """Format template with provided values."""
    try:
        return template.format(**kwargs)
    except KeyError as e:
        return f"Template error: Missing key {e}"


# ============================================================================
# CONTEXTUAL STATEMENTS
# ============================================================================

CONTEXT_STATEMENTS = {
    'sales_revenue_drop': "This decline may indicate market saturation, competitive pressure, or seasonal effects.",
    'sales_revenue_spike': "This increase suggests successful initiatives, market expansion, or favorable conditions.",
    'cost_increase': "Rising costs may compress margins and require pricing or efficiency adjustments.",
    'efficiency_gain': "Improved efficiency can enhance profitability and competitive position.",
    'customer_churn': "Increased churn threatens revenue stability and growth prospects.",
    'engagement_drop': "Declining engagement may predict future churn or reduced lifetime value.",
}


def get_context_statement(insight_type, domain='general'):
    """Get contextual explanation for insight type."""
    return CONTEXT_STATEMENTS.get(insight_type, "Further investigation recommended.")
