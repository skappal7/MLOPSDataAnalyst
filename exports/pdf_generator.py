"""PDF Generator - Create formatted PDF reports"""
from typing import List, Dict, Any
from io import BytesIO
from datetime import datetime

class PDFGenerator:
    def generate(self, insights: List[Dict[str, Any]], config: Dict[str, Any]) -> bytes:
        """Generate PDF report using HTML/CSS."""
        
        try:
            from weasyprint import HTML, CSS
            from jinja2 import Template
        except ImportError:
            # Fallback if WeasyPrint not available
            return self._generate_simple_pdf(insights, config)
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                @page {
                    size: A4;
                    margin: 2cm;
                }
                body {
                    font-family: 'Arial', sans-serif;
                    line-height: 1.6;
                    color: #333;
                }
                h1 {
                    color: #2c3e50;
                    border-bottom: 4px solid #3498db;
                    padding-bottom: 10px;
                    margin-bottom: 30px;
                }
                h2 {
                    color: #34495e;
                    margin-top: 40px;
                    margin-bottom: 20px;
                    border-left: 5px solid #3498db;
                    padding-left: 15px;
                }
                h3 {
                    color: #2c3e50;
                    margin-top: 25px;
                }
                .header {
                    text-align: center;
                    margin-bottom: 40px;
                }
                .summary-box {
                    background: #f8f9fa;
                    padding: 20px;
                    border-left: 5px solid #3498db;
                    margin: 20px 0;
                }
                .insight {
                    margin: 25px 0;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    page-break-inside: avoid;
                }
                .insight-high {
                    border-left: 5px solid #e74c3c;
                    background: #fee;
                }
                .insight-medium {
                    border-left: 5px solid #f39c12;
                    background: #fef9e7;
                }
                .insight-low {
                    border-left: 5px solid #3498db;
                    background: #ebf5fb;
                }
                .score {
                    display: inline-block;
                    padding: 5px 12px;
                    border-radius: 3px;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                }
                .score-high { background: #e74c3c; }
                .score-medium { background: #f39c12; }
                .score-low { background: #3498db; }
                .metric-value {
                    color: #2980b9;
                    font-weight: bold;
                    font-size: 1.1em;
                }
                .data-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                }
                .data-table th {
                    background: #34495e;
                    color: white;
                    padding: 10px;
                    text-align: left;
                }
                .data-table td {
                    padding: 8px;
                    border-bottom: 1px solid #ddd;
                }
                .footer {
                    margin-top: 50px;
                    padding-top: 20px;
                    border-top: 2px solid #3498db;
                    text-align: center;
                    font-size: 12px;
                    color: #7f8c8d;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Data Analysis Report</h1>
                <p><strong>Generated:</strong> {{ date }}</p>
                <p><strong>Analysis Type:</strong> {{ domain }}</p>
            </div>
            
            <div class="summary-box">
                <h2>Executive Summary</h2>
                <p><strong>Total Insights Found:</strong> {{ total_insights }}</p>
                <p><strong>High Priority:</strong> {{ high_priority }} | 
                   <strong>Medium Priority:</strong> {{ medium_priority }} | 
                   <strong>Low Priority:</strong> {{ low_priority }}</p>
            </div>
            
            <h2>Key Findings</h2>
            
            {% for insight in insights[:15] %}
            <div class="insight insight-{{ insight.priority }}">
                <h3>{{ loop.index }}. {{ insight.title }}
                    <span class="score score-{{ insight.priority }}">{{ "%.1f"|format(insight.score) }}/10</span>
                </h3>
                
                <div style="margin: 15px 0;">
                    {{ insight.narrative }}
                </div>
                
                {% if insight.data %}
                <div style="margin-top: 15px; font-size: 0.9em; color: #555;">
                    <strong>Details:</strong>
                    <ul style="margin: 5px 0; padding-left: 20px;">
                    {% for key, value in insight.data.items() %}
                        {% if key not in ['chart', 'raw_data'] %}
                        <li><strong>{{ key|replace('_', ' ')|title }}:</strong> {{ value }}</li>
                        {% endif %}
                    {% endfor %}
                    </ul>
                </div>
                {% endif %}
            </div>
            {% endfor %}
            
            <div class="footer">
                <p>Generated by Intelligent Data Analyzer | Powered by Polars, DuckDB, and Statistical Analysis</p>
                <p>This is an automated report. Please verify critical findings.</p>
            </div>
        </body>
        </html>
        """
        
        # Prepare data for template
        high_priority = len([i for i in insights if i['score'] >= 8])
        medium_priority = len([i for i in insights if 6 <= i['score'] < 8])
        low_priority = len([i for i in insights if i['score'] < 6])
        
        # Classify insights by priority
        for insight in insights:
            if insight['score'] >= 8:
                insight['priority'] = 'high'
            elif insight['score'] >= 6:
                insight['priority'] = 'medium'
            else:
                insight['priority'] = 'low'
        
        # Render template
        template = Template(html_template)
        html_content = template.render(
            insights=insights,
            total_insights=len(insights),
            high_priority=high_priority,
            medium_priority=medium_priority,
            low_priority=low_priority,
            date=datetime.now().strftime("%Y-%m-%d %H:%M"),
            domain=config.get('domain', 'General Analysis')
        )
        
        # Generate PDF
        try:
            pdf_bytes = HTML(string=html_content).write_pdf()
            return pdf_bytes
        except Exception as e:
            print(f"Error generating PDF with WeasyPrint: {e}")
            return self._generate_simple_pdf(insights, config)
    
    def _generate_simple_pdf(self, insights: List[Dict[str, Any]], config: Dict[str, Any]) -> bytes:
        """Fallback simple text-based PDF."""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor='#2c3e50',
                spaceAfter=30
            )
            story.append(Paragraph("Data Analysis Report", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Summary
            summary_text = f"""
            <b>Generated:</b> {datetime.now().strftime("%Y-%m-%d %H:%M")}<br/>
            <b>Total Insights:</b> {len(insights)}<br/>
            <b>High Priority:</b> {len([i for i in insights if i['score'] >= 8])}
            """
            story.append(Paragraph(summary_text, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # Insights
            for idx, insight in enumerate(insights[:15], 1):
                story.append(Paragraph(f"<b>{idx}. {insight['title']}</b> (Score: {insight['score']:.1f}/10)", 
                                      styles['Heading3']))
                story.append(Paragraph(insight.get('narrative', 'No description'), styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
            
            doc.build(story)
            pdf_bytes = buffer.getvalue()
            buffer.close()
            return pdf_bytes
            
        except ImportError:
            # Ultimate fallback - return text
            text_content = "DATA ANALYSIS REPORT\n\n"
            text_content += f"Generated: {datetime.now()}\n\n"
            for idx, insight in enumerate(insights[:15], 1):
                text_content += f"{idx}. {insight['title']} (Score: {insight['score']:.1f})\n"
                text_content += f"   {insight.get('narrative', '')}\n\n"
            return text_content.encode('utf-8')
