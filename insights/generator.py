"""Narrative Generator - Create human-readable insights"""
from typing import List, Dict, Any
from config.narrative_templates import get_template, format_template

class NarrativeGenerator:
    def generate_narratives(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate narratives for all insights."""
        for insight in insights:
            insight['narrative'] = self._generate_narrative(insight)
        return insights
    
    def _generate_narrative(self, insight: Dict[str, Any]) -> str:
        """Generate narrative for single insight."""
        insight_type = insight.get('type', 'generic')
        data = insight.get('data', {})
        
        # Correlation narratives
        if insight_type == 'correlation':
            return self._correlation_narrative(data)
        
        # Distribution narratives
        elif insight_type == 'distribution':
            return self._distribution_narrative(data)
        
        # Variability narratives
        elif insight_type == 'variability':
            return self._variability_narrative(data)
        
        # Skewness narratives
        elif insight_type == 'skewness':
            return self._skewness_narrative(data)
        
        # Time series narratives
        elif insight_type == 'trend':
            return self._trend_narrative(data)
        
        elif insight_type == 'growth_change':
            return self._growth_change_narrative(data)
        
        elif insight_type == 'high_volatility':
            return self._volatility_narrative(data)
        
        elif insight_type == 'volatility_spike':
            return self._volatility_spike_narrative(data)
        
        # Categorical narratives
        elif insight_type == 'segment_divergence':
            return self._segment_divergence_narrative(data)
        
        elif insight_type == 'high_concentration':
            return self._concentration_narrative(data)
        
        # Anomaly narratives
        elif insight_type in ['outliers_zscore', 'outliers_iqr']:
            return self._outlier_narrative(data)
        
        elif insight_type == 'multivariate_anomalies':
            return self._multivariate_anomaly_narrative(data)
        
        # Generic fallback
        return "Significant pattern detected. Further investigation recommended."
    
    def _correlation_narrative(self, data: Dict[str, Any]) -> str:
        """Generate correlation narrative."""
        var1 = data.get('var1', 'Variable 1')
        var2 = data.get('var2', 'Variable 2')
        corr = data.get('correlation', 0)
        p_value = data.get('p_value', 1)
        strength = data.get('strength', 'moderate')
        direction = data.get('direction', 'positive')
        
        narrative = f"**{strength.capitalize()} {direction} correlation detected** between **{var1}** and **{var2}** (r = {corr:.3f}).\n\n"
        
        if direction == 'positive':
            narrative += f"This means when {var1} increases, {var2} tends to increase proportionally. "
        else:
            narrative += f"This means when {var1} increases, {var2} tends to decrease. "
        
        if p_value < 0.01:
            narrative += "This relationship is **highly statistically significant** (p < 0.01).\n\n"
        elif p_value < 0.05:
            narrative += "This relationship is **statistically significant** (p < 0.05).\n\n"
        
        narrative += "**Implication:** This relationship should be considered in decision-making and forecasting models."
        
        return narrative
    
    def _distribution_narrative(self, data: Dict[str, Any]) -> str:
        """Generate distribution narrative."""
        metric = data.get('metric', 'Metric')
        dist_type = data.get('distribution_type', 'Non-normal')
        skewness = data.get('skewness', 0)
        kurtosis = data.get('kurtosis', 0)
        
        narrative = f"**{metric}** exhibits a **{dist_type.lower()} distribution**, which deviates from the normal (bell curve) pattern.\n\n"
        
        if abs(skewness) > 1:
            if skewness > 0:
                narrative += f"The distribution is **right-skewed** (skewness = {skewness:.2f}), meaning there are more extreme high values than expected. "
            else:
                narrative += f"The distribution is **left-skewed** (skewness = {skewness:.2f}), meaning there are more extreme low values than expected. "
        
        if abs(kurtosis) > 1:
            if kurtosis > 0:
                narrative += f"The distribution has **heavy tails** (kurtosis = {kurtosis:.2f}), indicating more extreme values than a normal distribution."
            else:
                narrative += f"The distribution has **light tails** (kurtosis = {kurtosis:.2f}), indicating fewer extreme values than normal."
        
        narrative += "\n\n**Implication:** Standard statistical methods assuming normality may not be appropriate. Consider using non-parametric methods or data transformation."
        
        return narrative
    
    def _variability_narrative(self, data: Dict[str, Any]) -> str:
        """Generate variability narrative."""
        metric = data.get('metric', 'Metric')
        cv = data.get('coefficient_of_variation', 0)
        
        narrative = f"**{metric}** shows **high variability** relative to its average value (CV = {cv:.1f}%).\n\n"
        narrative += f"The data is highly dispersed, making predictions and trends less reliable. "
        narrative += "This high variability could indicate:\n"
        narrative += "- Multiple distinct populations in the data\n"
        narrative += "- Seasonal or cyclical effects\n"
        narrative += "- External factors causing instability\n\n"
        narrative += "**Recommendation:** Investigate subgroups or time periods separately for more stable patterns."
        
        return narrative
    
    def _skewness_narrative(self, data: Dict[str, Any]) -> str:
        """Generate skewness narrative."""
        metric = data.get('metric', 'Metric')
        mean = data.get('mean', 0)
        median = data.get('median', 0)
        
        narrative = f"**{metric}** shows an **asymmetric distribution** where the mean ({mean:.2f}) differs significantly from the median ({median:.2f}).\n\n"
        
        if mean > median:
            narrative += "The mean is higher than the median, indicating a **right-skewed** distribution with some extreme high values pulling the average up. "
        else:
            narrative += "The mean is lower than the median, indicating a **left-skewed** distribution with some extreme low values pulling the average down. "
        
        narrative += "\n\n**Implication:** The median may be a more representative measure of central tendency than the mean for this metric."
        
        return narrative
    
    def _trend_narrative(self, data: Dict[str, Any]) -> str:
        """Generate trend narrative."""
        metric = data.get('metric', 'Metric')
        trend = data.get('trend', 'upward')
        strength = data.get('strength', 'moderate')
        r_squared = data.get('r_squared', 0)
        pct_change = data.get('pct_change_per_period', 0)
        
        narrative = f"**{strength.capitalize()} {trend} trend detected** in **{metric}** (R² = {r_squared:.3f}).\n\n"
        
        if abs(pct_change) > 0:
            narrative += f"The metric is changing by approximately **{pct_change:+.1f}% per period** on average. "
        
        if r_squared > 0.7:
            narrative += "The trend is **very consistent** and predictable. "
        elif r_squared > 0.4:
            narrative += "The trend is **moderately consistent**. "
        
        narrative += f"\n\n**Implication:** If this {trend} trend continues, expect {'growth' if trend == 'upward' else 'decline'} in future periods."
        
        return narrative
    
    def _growth_change_narrative(self, data: Dict[str, Any]) -> str:
        """Generate growth change narrative."""
        metric = data.get('metric', 'Metric')
        change_type = data.get('change_type', 'acceleration')
        recent = data.get('recent_growth_rate', 0)
        earlier = data.get('earlier_growth_rate', 0)
        
        narrative = f"**Growth {change_type} detected** in **{metric}**.\n\n"
        narrative += f"Recent growth rate: **{recent:+.1f}%** compared to earlier: **{earlier:+.1f}%**\n\n"
        
        if change_type == 'acceleration':
            narrative += "Growth is speeding up, indicating positive momentum. "
        else:
            narrative += "Growth is slowing down, which may signal market saturation or headwinds. "
        
        narrative += "\n\n**Recommendation:** Monitor closely for continued trend or reversal."
        
        return narrative
    
    def _volatility_narrative(self, data: Dict[str, Any]) -> str:
        """Generate volatility narrative."""
        metric = data.get('metric', 'Metric')
        
        narrative = f"**{metric}** exhibits **high volatility** in its growth rates.\n\n"
        narrative += "The metric shows inconsistent period-over-period changes, making it difficult to predict future values. "
        narrative += "This could indicate:\n"
        narrative += "- Response to external market conditions\n"
        narrative += "- Seasonal business cycles\n"
        narrative += "- Operational instability\n\n"
        narrative += "**Recommendation:** Implement smoothing techniques or analyze by season/segment for clearer patterns."
        
        return narrative
    
    def _volatility_spike_narrative(self, data: Dict[str, Any]) -> str:
        """Generate volatility spike narrative."""
        metric = data.get('metric', 'Metric')
        num_spikes = data.get('num_spikes', 0)
        
        narrative = f"**Volatility spikes detected** in **{metric}** ({num_spikes} periods with unusual variability).\n\n"
        narrative += "These spikes represent periods where the metric fluctuated much more than usual. "
        narrative += "Investigate these periods for:\n"
        narrative += "- External events (market changes, competitor actions)\n"
        narrative += "- Internal changes (campaigns, pricing changes)\n"
        narrative += "- Data quality issues\n\n"
        narrative += "**Action:** Review specific spike periods to understand root causes."
        
        return narrative
    
    def _segment_divergence_narrative(self, data: Dict[str, Any]) -> str:
        """Generate segment divergence narrative."""
        dimension = data.get('dimension', 'Dimension')
        metric = data.get('metric', 'Metric')
        top_seg = data.get('top_segment', 'Top')
        top_val = data.get('top_value', 0)
        bottom_seg = data.get('bottom_segment', 'Bottom')
        bottom_val = data.get('bottom_value', 0)
        gap = data.get('gap_percentage', 0)
        
        narrative = f"**Significant performance gap** detected across **{dimension}** for **{metric}**.\n\n"
        narrative += f"**Top performer:** {top_seg} = {top_val:.2f}\n"
        narrative += f"**Bottom performer:** {bottom_seg} = {bottom_val:.2f}\n"
        narrative += f"**Gap:** {gap:+.1f}%\n\n"
        
        if gap > 100:
            narrative += "This **very large gap** suggests fundamentally different dynamics between segments. "
        elif gap > 50:
            narrative += "This **substantial gap** indicates significant opportunity for improvement in underperforming segments. "
        
        narrative += "\n\n**Recommendation:** Analyze top-performing segments for best practices to apply elsewhere."
        
        return narrative
    
    def _concentration_narrative(self, data: Dict[str, Any]) -> str:
        """Generate concentration narrative."""
        dimension = data.get('dimension', 'Dimension')
        top_3_pct = data.get('top_3_percentage', 0)
        
        narrative = f"**High concentration** detected in **{dimension}**.\n\n"
        narrative += f"The top 3 categories account for **{top_3_pct:.1f}%** of the total. "
        
        if top_3_pct > 80:
            narrative += "This **extreme concentration** indicates heavy dependency on a few categories. "
        else:
            narrative += "This concentration suggests limited diversity. "
        
        narrative += "\n\n**Risk:** High concentration increases vulnerability to changes in top categories.\n"
        narrative += "**Opportunity:** Potential to diversify and reduce dependency risk."
        
        return narrative
    
    def _outlier_narrative(self, data: Dict[str, Any]) -> str:
        """Generate outlier narrative."""
        metric = data.get('metric', 'Metric')
        method = data.get('method', 'Statistical')
        num_outliers = data.get('num_outliers', 0)
        outlier_pct = data.get('outlier_percentage', 0)
        
        narrative = f"**{num_outliers} outliers detected** in **{metric}** using {method} method ({outlier_pct:.1f}% of data).\n\n"
        narrative += "These values are statistically unusual and deviate significantly from the typical range. "
        narrative += "Outliers could represent:\n"
        narrative += "- Genuine extreme events worth investigating\n"
        narrative += "- Data entry errors\n"
        narrative += "- Special cases requiring separate treatment\n\n"
        narrative += "**Action:** Review outlier records to determine if they're valid or erroneous."
        
        return narrative
    
    def _multivariate_anomaly_narrative(self, data: Dict[str, Any]) -> str:
        """Generate multivariate anomaly narrative."""
        num_anomalies = data.get('num_anomalies', 0)
        metrics = data.get('metrics', [])
        
        narrative = f"**{num_anomalies} records with unusual patterns** detected across multiple metrics: {', '.join(metrics)}.\n\n"
        narrative += "These records have combinations of values that are statistically rare, even though individual values may seem normal. "
        narrative += "This could indicate:\n"
        narrative += "- Special customer segments or behaviors\n"
        narrative += "- Fraudulent or erroneous records\n"
        narrative += "- Unique business scenarios\n\n"
        narrative += "**Recommendation:** Investigate these records for insights or data quality issues."
        
        return narrative
