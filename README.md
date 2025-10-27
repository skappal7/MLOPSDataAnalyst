# Streamlit Data Analyzer

**Automated statistical analysis and insight generation for large datasets**

## 🎯 Features

- 🚀 **Fast Processing**: Polars + DuckDB for 200MB+ files
- 📊 **Smart Insights**: Context-aware statistical analysis
- 🎯 **Prioritized Findings**: Automated scoring and ranking
- 📄 **Multiple Exports**: PDF, Excel, HTML, Markdown
- 🔍 **50+ Column Support**: Mixed categorical and numerical data
- ⚡ **Zero LLM Dependency**: Pure ML and statistical methods

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/streamlit-data-analyzer.git
cd streamlit-data-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run Application

```bash
streamlit run app.py
```

Open browser at `http://localhost:8501`

## 📖 Usage

### Step 1: Upload Data
- Supported formats: CSV, Excel (.xlsx, .xls)
- Recommended size: Up to 200MB
- Columns: 50+ supported (mixed types)

### Step 2: Answer 5 Questions
The system asks strategic questions to guide analysis:
1. **Data Type** - Sales, Marketing, Operations, etc.
2. **Key Metrics** - Select up to 3 most important metrics
3. **Time Dimension** - Date column and granularity
4. **Comparison Type** - Period-over-period, segments, targets
5. **Alert Thresholds** - Define what's "unusual"

### Step 3: Review Insights
- High-priority findings (score ≥ 8)
- Medium-priority findings (score 6-7)
- Detailed analysis with charts and data

### Step 4: Export Reports
- **PDF**: Formatted professional report
- **Excel**: Tables with conditional formatting
- **Markdown**: Structured text format
- **HTML**: Interactive charts and tables

## 🏗️ Architecture

```
Polars (Fast Ingestion) 
  → Parquet (Columnar Storage) 
  → DuckDB (SQL Analytics) 
  → Statistical Analysis (scipy/sklearn) 
  → Scored Insights 
  → Multi-format Export
```

## 📁 Project Structure

```
streamlit-data-analyzer/
├── app.py                    # Main application
├── requirements.txt          # Dependencies
├── config/                   # Configuration & templates
├── core/                     # Data processing & profiling
├── analyzers/                # Statistical & ML analysis
├── insights/                 # Scoring & narrative generation
├── exports/                  # Report generators
└── utils/                    # Utilities
```

## 🔧 Key Technologies

- **Polars**: High-performance data processing (5-10x faster than pandas)
- **DuckDB**: In-process analytical database (optimized for analytics)
- **Streamlit**: Interactive web interface
- **scipy/statsmodels**: Statistical testing and time-series analysis
- **scikit-learn**: Machine learning insights (clustering, anomaly detection)

## 📊 Analysis Capabilities

### Statistical Analysis
- Correlation detection
- Distribution analysis
- Hypothesis testing
- Outlier detection

### Time Series
- Trend analysis
- Seasonality detection
- Change point detection
- Growth rate calculation

### Categorical Analysis
- Segment comparison
- Chi-square tests
- Distribution shifts
- Concentration analysis

### ML Insights
- Clustering (DBSCAN, K-means)
- Anomaly detection
- Dimensionality reduction (PCA)
- Pattern recognition

## ⚙️ Requirements

- Python 3.11+
- 4GB+ RAM (recommended for large datasets)
- Modern browser (Chrome, Firefox, Edge)

## 📝 Example Use Cases

### Sales Analysis
```
- Upload: sales_data.csv (2M rows, 40 columns)
- Domain: Sales/Revenue
- Key Metrics: Revenue, Units, Profit
- Time: Monthly analysis
- Output: Q4 revenue drop of 23% detected with segment breakdowns
```

### Customer Behavior
```
- Upload: customer_events.xlsx (500K rows, 25 columns)
- Domain: Customer Behavior
- Key Metrics: Engagement, LTV, Churn Rate
- Output: Unusual churn pattern in Segment B identified
```

## 🐛 Troubleshooting

### Memory Issues
- Reduce file size or sample data
- Close other applications
- Increase system RAM if possible

### Slow Performance
- Convert to Parquet format manually first
- Reduce number of columns if not needed
- Use time-based filtering to analyze subsets

### Missing Dependencies
```bash
pip install --upgrade -r requirements.txt
```

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

Built with:
- Streamlit
- Polars
- DuckDB
- scipy/statsmodels
- scikit-learn

## 📧 Support

- Issues: GitHub Issues
- Discussions: GitHub Discussions
- Email: your-email@example.com

---

**Made with ❤️ for data analysts who want automated, intelligent insights**
