"""Advanced professional report generation with AI summaries."""
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak,
    Table, TableStyle, KeepTogether
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
import io
import logging

logger = logging.getLogger(__name__)


class AdvancedReportGenerator:
    """Generate professional financial reports with AI summaries."""

    def __init__(self, output_dir: Path, llm_handler=None):
        """Initialize advanced report generator.

        Args:
            output_dir: Directory to save generated reports
            llm_handler: LLM handler for generating summaries
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.llm_handler = llm_handler
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Set up custom professional report styles."""
        # Header style
        self.styles.add(ParagraphStyle(
            name='ReportHeader',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1a365d'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Company name style
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c5282'),
            spaceAfter=4,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))

        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#2c5282'),
            spaceAfter=12,
            spaceBefore=16,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=colors.HexColor('#2c5282'),
            borderPadding=6
        ))

        # Executive summary
        self.styles.add(ParagraphStyle(
            name='ExecutiveSummary',
            parent=self.styles['BodyText'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leading=14
        ))

        # Metadata
        self.styles.add(ParagraphStyle(
            name='Metadata',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#4a5568'),
            spaceAfter=2,
            alignment=TA_CENTER
        ))

        # KPI Label
        self.styles.add(ParagraphStyle(
            name='KPILabel',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#4a5568'),
            spaceAfter=2
        ))

        # KPI Value
        self.styles.add(ParagraphStyle(
            name='KPIValue',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#1a365d'),
            fontName='Helvetica-Bold',
            spaceAfter=8
        ))

    def generate_executive_summary(self, data: pd.DataFrame, query_context: str) -> str:
        """Generate AI-powered executive summary.

        Args:
            data: DataFrame with financial data
            query_context: Context about the query

        Returns:
            Executive summary text
        """
        if self.llm_handler is None:
            return self._generate_basic_summary(data)

        try:
            # Prepare data summary for LLM
            data_summary = self._prepare_data_summary(data)

            # Create prompt for LLM
            prompt = f"""You are a business analyst writing an executive summary for a strategic report. Generate a comprehensive, narrative-driven analysis that tells the story behind the data.

Context: {query_context}

Data Summary:
- Total Records: {len(data)}
- Columns: {', '.join(data.columns.tolist())}

Key Statistics:
{data_summary}

Sample Data (first 5 rows):
{data.head().to_string()}

Requirements:
1. Write 2-3 cohesive paragraphs (6-9 sentences) that form a narrative
2. Tell a STORY about what this data reveals about the business
3. Connect data points to paint a complete picture
4. Reference SPECIFIC NUMBERS naturally within the narrative flow
5. Explain WHY the numbers matter and what they indicate about business health
6. Identify cause-and-effect relationships between metrics
7. Discuss strategic implications: opportunities, risks, trends, competitive positioning
8. Use narrative language: "This analysis reveals a compelling story...", "The data paints a picture of...", "These findings suggest a broader trend where..."
9. Make comparisons and contextual observations (e.g., "significantly higher than industry average", "indicates strong momentum")
10. Do NOT mention SQL, queries, or technical database terms
11. Write as if presenting to C-suite executives who need strategic context, not just numbers

Think: What story does this data tell? What should leaders understand? What actions might this suggest?

Executive Summary:"""

            # Get summary from LLM
            result = self.llm_handler.query(prompt)
            summary = result.get('answer', '')

            # Clean up the summary - remove any technical prefixes (re imported at top)
            summary = summary.replace('Executive Summary:', '').strip()
            # Remove SQLQuery anywhere in the text (not just at start)
            summary = re.sub(r'SQLQuery:\s*', '', summary, flags=re.IGNORECASE | re.MULTILINE)
            summary = re.sub(r'SQL\s*[Qq]uery:\s*', '', summary, flags=re.IGNORECASE | re.MULTILINE)
            # Remove any trailing error messages
            if 'Background on this error' in summary or 'sqlalche.me' in summary:
                # Split at error message and take only the part before
                summary = re.split(r'\(Background on this error|https://sqlalche\.me', summary)[0]
            summary = summary.strip()

            return summary if summary else self._generate_basic_summary(data)

        except Exception as e:
            logger.error(f"Error generating AI summary: {str(e)}")
            return self._generate_basic_summary(data)

    def _prepare_data_summary(self, df: pd.DataFrame) -> str:
        """Prepare comprehensive statistical summary of data.

        Args:
            df: Input DataFrame

        Returns:
            Formatted summary string with detailed statistics
        """
        summary_parts = []

        # Numeric columns summary with enhanced statistics
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols[:5]:  # Limit to first 5 numeric columns
            total = df[col].sum()
            mean = df[col].mean()
            median = df[col].median()
            std = df[col].std()
            min_val = df[col].min()
            max_val = df[col].max()

            summary_parts.append(
                f"- {col}:\n"
                f"  Total: {total:,.2f}, Average: {mean:,.2f}, Median: {median:,.2f}\n"
                f"  Range: {min_val:,.2f} to {max_val:,.2f}, Std Dev: {std:,.2f}"
            )

        # Categorical columns summary with value counts
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols[:3]:  # Limit to first 3 categorical columns
            unique_count = df[col].nunique()
            top_value = df[col].mode()[0] if len(df[col].mode()) > 0 else "N/A"
            top_count = df[col].value_counts().iloc[0] if len(df[col]) > 0 else 0
            top_percentage = (top_count / len(df) * 100) if len(df) > 0 else 0

            summary_parts.append(
                f"- {col}: {unique_count} unique values\n"
                f"  Most common: '{top_value}' ({top_count} occurrences, {top_percentage:.1f}%)"
            )

        return '\n'.join(summary_parts)

    def _generate_basic_summary(self, df: pd.DataFrame) -> str:
        """Generate basic summary without LLM.

        Args:
            df: Input DataFrame

        Returns:
            Basic summary text
        """
        summary = f"""This report presents an analysis of {len(df)} records across {len(df.columns)} data fields. """

        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            summary += f"The dataset includes {len(numeric_cols)} numerical metrics providing quantitative insights. "

        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            summary += f"Additionally, {len(categorical_cols)} categorical dimensions enable segmentation and comparative analysis."

        return summary

    def _generate_insights(self, data: pd.DataFrame, query_context: str) -> str:
        """Generate AI-powered insights and analysis.

        Args:
            data: DataFrame with financial data
            query_context: Context about the query

        Returns:
            Insights and analysis text
        """
        if self.llm_handler is None:
            return self._generate_basic_insights(data)

        try:
            # Prepare data summary for LLM
            data_summary = self._prepare_data_summary(data)

            # Create prompt for LLM to generate insights
            prompt = f"""You are a strategic business consultant analyzing data for C-level executives. Generate 4 narrative-driven insights that tell the story of what this data means for the business.

Context: {query_context}

Data Summary:
- Total Records: {len(data)}
- Columns: {', '.join(data.columns.tolist())}

Key Statistics:
{data_summary}

Sample Data (first 5 rows):
{data.head().to_string()}

Requirements:
1. Generate EXACTLY 4 numbered insights (1., 2., 3., 4.)
2. Each insight should be 3-5 sentences forming a cohesive narrative
3. START each insight with a compelling, descriptive heading that captures the key finding
4. Weave SPECIFIC NUMBERS naturally into the narrative (don't just list them)
5. Tell the STORY: What does this metric reveal? Why does it matter? What's the impact?
6. Connect the dots: Show relationships between different data points
7. Provide CONTEXT: Compare to benchmarks, identify if it's good/bad/concerning
8. Explain strategic implications: What opportunities or risks does this create?
9. Recommend actions: What should leadership consider doing based on this finding?
10. Use narrative language: "The data reveals a critical pattern...", "This finding suggests...", "When viewed together, these metrics indicate..."
11. Make it human-readable: Write as if you're explaining to a CEO in a meeting
12. Format as: "1. [Bold Compelling Heading]: [Narrative analysis that connects data to business strategy and outcomes]"
13. Do NOT mention SQL, queries, or technical database terms

Think: If you had 2 minutes with the CEO, what would you tell them about each finding? Why should they care? What should they do?

Key Insights:"""

            # Get insights from LLM
            result = self.llm_handler.query(prompt)
            insights = result.get('answer', '')

            # Clean up the insights
            insights = insights.replace('Key Insights & Findings:', '').strip()
            insights = insights.replace('Key Insights:', '').strip()

            # Remove any error messages that got included
            if 'Background on this error' in insights or 'sqlalche.me' in insights:
                # Split at error message and take only the part before
                insights = re.split(r'\(Background on this error|https://sqlalche\.me', insights)[0]
                insights = insights.strip()

            # Remove any lines that contain error text
            lines = insights.split('\n')
            cleaned_lines = []
            for line in lines:
                # Skip lines with error messages
                if 'error' not in line.lower() or re.match(r'^\d+\.', line.strip()):
                    cleaned_lines.append(line)
            insights = '\n'.join(cleaned_lines).strip()

            return insights if insights else self._generate_basic_insights(data)

        except Exception as e:
            logger.error(f"Error generating AI insights: {str(e)}")
            return self._generate_basic_insights(data)

    def _generate_basic_insights(self, df: pd.DataFrame) -> str:
        """Generate basic insights without LLM.

        Args:
            df: Input DataFrame

        Returns:
            Basic insights text
        """
        insights = []

        # Data volume insight
        insights.append(f"The dataset contains {len(df):,} records across {len(df.columns)} dimensions, providing a comprehensive view for analysis.")

        # Numeric columns insight
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            col = numeric_cols[0]
            total = df[col].sum()
            avg = df[col].mean()
            insights.append(f"Key metric '{col.replace('_', ' ').title()}' shows a total value of {total:,.2f} with an average of {avg:,.2f} per record.")

        # Categorical insight
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            col = categorical_cols[0]
            unique_count = df[col].nunique()
            insights.append(f"The data includes {unique_count} distinct categories in the '{col.replace('_', ' ').title()}' dimension, enabling detailed segmentation analysis.")

        return ' '.join(insights)

    def _auto_generate_charts(self, data: pd.DataFrame) -> List[go.Figure]:
        """Automatically generate relevant charts based on data characteristics.

        Args:
            data: Input DataFrame

        Returns:
            List of generated Plotly figures
        """
        charts = []

        try:
            # Identify numeric and categorical columns
            numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = data.select_dtypes(include=['object']).columns.tolist()

            # Chart 1: Top values bar chart (if we have categorical + numeric)
            if len(categorical_cols) > 0 and len(numeric_cols) > 0:
                cat_col = categorical_cols[0]
                num_col = numeric_cols[0]

                # Aggregate data
                if len(data) > 15:
                    # Show top 10 for large datasets
                    agg_data = data.groupby(cat_col)[num_col].sum().nlargest(10).sort_values(ascending=True)
                else:
                    agg_data = data.groupby(cat_col)[num_col].sum().sort_values(ascending=True)

                fig1 = go.Figure(data=[
                    go.Bar(
                        x=agg_data.values,
                        y=agg_data.index,
                        orientation='h',
                        marker=dict(color='#2c5282'),
                        text=agg_data.values,
                        texttemplate='%{text:,.0f}',
                        textposition='auto'
                    )
                ])
                fig1.update_layout(
                    title=f"Top {cat_col.replace('_', ' ').title()} by {num_col.replace('_', ' ').title()}",
                    xaxis_title=num_col.replace('_', ' ').title(),
                    yaxis_title=cat_col.replace('_', ' ').title(),
                    height=400,
                    showlegend=False,
                    plot_bgcolor='white'
                )
                charts.append(fig1)

            # Chart 2: Distribution chart (if we have multiple numeric columns)
            if len(numeric_cols) >= 2:
                num_col1 = numeric_cols[0]
                num_col2 = numeric_cols[1]

                fig2 = go.Figure(data=[
                    go.Scatter(
                        x=data[num_col1],
                        y=data[num_col2],
                        mode='markers',
                        marker=dict(
                            size=8,
                            color='#636EFA',
                            opacity=0.6,
                            line=dict(width=1, color='white')
                        )
                    )
                ])
                fig2.update_layout(
                    title=f"{num_col1.replace('_', ' ').title()} vs {num_col2.replace('_', ' ').title()}",
                    xaxis_title=num_col1.replace('_', ' ').title(),
                    yaxis_title=num_col2.replace('_', ' ').title(),
                    height=400,
                    showlegend=False,
                    plot_bgcolor='white'
                )
                charts.append(fig2)

            # Chart 3: Category distribution pie chart
            if len(categorical_cols) > 0:
                cat_col = categorical_cols[0]
                value_counts = data[cat_col].value_counts().head(8)

                fig3 = go.Figure(data=[
                    go.Pie(
                        labels=value_counts.index,
                        values=value_counts.values,
                        hole=0.4,
                        marker=dict(colors=['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880'])
                    )
                ])
                fig3.update_layout(
                    title=f"Distribution by {cat_col.replace('_', ' ').title()}",
                    height=400,
                    showlegend=True
                )
                charts.append(fig3)

        except Exception as e:
            logger.error(f"Error auto-generating charts: {str(e)}")

        return charts

    def generate_report_content(
        self,
        company_name: str,
        report_title: str,
        data: pd.DataFrame,
        query_context: str = "",
        charts: Optional[List[go.Figure]] = None,
        include_kpis: bool = True,
        include_executive_summary: bool = True,
        auto_generate_charts: bool = True
    ) -> Dict[str, Any]:
        """Generate report content for display in chat (not PDF).

        Args:
            company_name: Name of the company/entity
            report_title: Title of the report
            data: DataFrame containing the report data
            query_context: Context about the data query
            charts: List of Plotly figures to include
            include_kpis: Whether to include KPI section
            include_executive_summary: Whether to include executive summary
            auto_generate_charts: Whether to auto-generate charts

        Returns:
            Dictionary containing report sections for chat display
        """
        report_content = {
            'company_name': company_name,
            'report_title': report_title,
            'date': datetime.now().strftime("%B %d, %Y"),
            'time': datetime.now().strftime("%I:%M %p"),
            'sections': {}
        }

        # Generate executive summary
        if include_executive_summary:
            summary_text = self.generate_executive_summary(data, query_context)
            report_content['sections']['executive_summary'] = summary_text

        # Generate data overview
        overview_text = f"This analysis encompasses {len(data):,} records across {len(data.columns)} key dimensions. "
        numeric_cols = data.select_dtypes(include=['number']).columns
        categorical_cols = data.select_dtypes(include=['object']).columns
        overview_text += f"The dataset includes {len(numeric_cols)} quantitative metrics and {len(categorical_cols)} categorical attributes."
        report_content['sections']['data_overview'] = overview_text

        # Generate KPIs
        if include_kpis and not data.empty:
            kpi_data = self._generate_kpis(data)
            report_content['sections']['kpis'] = kpi_data

        # Generate insights
        insights_text = self._generate_insights(data, query_context)
        # Clean up markdown
        insights_text = insights_text.replace('**', '')
        report_content['sections']['insights'] = insights_text

        # Auto-generate charts if needed
        if auto_generate_charts and not charts and not data.empty:
            charts = self._auto_generate_charts(data)

        report_content['charts'] = charts if charts else []

        return report_content

    def generate_professional_report(
        self,
        company_name: str,
        report_title: str,
        data: pd.DataFrame,
        query_context: str = "",
        charts: Optional[List[go.Figure]] = None,
        include_kpis: bool = True,
        include_executive_summary: bool = True,
        auto_generate_charts: bool = True
    ) -> str:
        """Generate a comprehensive professional report.

        Args:
            company_name: Name of the company/entity
            report_title: Title of the report
            data: DataFrame containing the report data
            query_context: Context about the data query
            charts: List of Plotly figures to include
            include_kpis: Whether to include KPI section
            include_executive_summary: Whether to include executive summary

        Returns:
            Path to the generated PDF report
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"professional_report_{timestamp}.pdf"
        filepath = self.output_dir / filename

        # Create PDF document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )

        elements = []

        # === HEADER SECTION ===
        elements.append(Paragraph(company_name, self.styles['CompanyName']))
        elements.append(Spacer(1, 0.1 * inch))
        elements.append(Paragraph(report_title, self.styles['ReportHeader']))
        elements.append(Spacer(1, 0.05 * inch))

        # Metadata
        report_date = datetime.now().strftime("%B %d, %Y")
        report_time = datetime.now().strftime("%I:%M %p")
        elements.append(Paragraph(f"Report Date: {report_date}", self.styles['Metadata']))
        elements.append(Paragraph(f"Generated: {report_time}", self.styles['Metadata']))
        elements.append(Spacer(1, 0.3 * inch))

        # === EXECUTIVE SUMMARY ===
        if include_executive_summary:
            elements.append(Paragraph("Executive Summary", self.styles['SectionHeading']))
            elements.append(Spacer(1, 0.15 * inch))

            summary_text = self.generate_executive_summary(data, query_context)

            # Split into paragraphs for better formatting
            paragraphs = summary_text.split('\n\n') if '\n\n' in summary_text else [summary_text]
            for para in paragraphs:
                if para.strip():
                    elements.append(Paragraph(para.strip(), self.styles['ExecutiveSummary']))
                    elements.append(Spacer(1, 0.1 * inch))

            elements.append(Spacer(1, 0.15 * inch))

        # === DATA OVERVIEW ===
        elements.append(Paragraph("Data Overview", self.styles['SectionHeading']))
        elements.append(Spacer(1, 0.1 * inch))

        overview_text = f"This analysis encompasses {len(data):,} records across {len(data.columns)} key dimensions. "
        numeric_cols = data.select_dtypes(include=['number']).columns
        categorical_cols = data.select_dtypes(include=['object']).columns
        overview_text += f"The dataset includes {len(numeric_cols)} quantitative metrics and {len(categorical_cols)} categorical attributes."

        elements.append(Paragraph(overview_text, self.styles['ExecutiveSummary']))
        elements.append(Spacer(1, 0.2 * inch))

        # === KEY METRICS / KPIs ===
        if include_kpis and not data.empty:
            elements.append(Paragraph("Key Performance Metrics", self.styles['SectionHeading']))
            elements.append(Spacer(1, 0.1 * inch))

            kpi_data = self._generate_kpis(data)
            if kpi_data:
                kpi_table = self._create_kpi_table(kpi_data)
                elements.append(kpi_table)
                elements.append(Spacer(1, 0.2 * inch))

        # === INSIGHTS SECTION ===
        # Generate AI-powered insights instead of showing raw data table
        elements.append(Paragraph("Key Insights & Analysis", self.styles['SectionHeading']))
        elements.append(Spacer(1, 0.15 * inch))

        insights_text = self._generate_insights(data, query_context)

        # Format insights - handle both paragraphs and numbered lists
        if insights_text:
            import re
            # Clean up any markdown bold markers
            insights_text = insights_text.replace('**', '')

            # Check if it's a numbered list
            if re.search(r'^\d+\.', insights_text.strip(), re.MULTILINE):
                # Split by numbered points and process
                lines = insights_text.split('\n')
                current_insight = ""
                insight_number = 0

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # Check if line starts with a number
                    match = re.match(r'^(\d+)\.\s*(.+)', line)
                    if match:
                        # Save previous insight if exists
                        if current_insight:
                            bullet_text = f"<b>{insight_number}.</b> {current_insight.strip()}"
                            elements.append(Paragraph(bullet_text, self.styles['ExecutiveSummary']))
                            elements.append(Spacer(1, 0.12 * inch))

                        # Start new insight
                        insight_number = int(match.group(1))
                        current_insight = match.group(2)
                    else:
                        # Continuation of current insight
                        if current_insight:
                            current_insight += " " + line

                # Add last insight
                if current_insight:
                    bullet_text = f"<b>{insight_number}.</b> {current_insight.strip()}"
                    elements.append(Paragraph(bullet_text, self.styles['ExecutiveSummary']))
                    elements.append(Spacer(1, 0.12 * inch))
            else:
                # Regular paragraphs
                paragraphs = insights_text.split('\n\n') if '\n\n' in insights_text else [insights_text]
                for para in paragraphs:
                    if para.strip():
                        elements.append(Paragraph(para.strip(), self.styles['ExecutiveSummary']))
                        elements.append(Spacer(1, 0.12 * inch))

        elements.append(Spacer(1, 0.2 * inch))

        # === VISUALIZATIONS ===
        # Auto-generate charts if enabled and none provided
        if auto_generate_charts and not charts and not data.empty:
            charts = self._auto_generate_charts(data)

        if charts:
            elements.append(PageBreak())
            elements.append(Paragraph("Visual Analysis & Trends", self.styles['SectionHeading']))
            elements.append(Spacer(1, 0.15 * inch))

            for i, fig in enumerate(charts):
                try:
                    # Convert Plotly figure to image
                    img_bytes = fig.to_image(format="png", width=750, height=450)
                    img = Image(io.BytesIO(img_bytes), width=7 * inch, height=4.2 * inch)
                    elements.append(img)
                    elements.append(Spacer(1, 0.4 * inch))
                except Exception as e:
                    logger.error(f"Error adding chart {i}: {str(e)}")

        # === FOOTER ===
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(Paragraph(
            f"<i>This report was generated automatically on {report_date} at {report_time}</i>",
            self.styles['Metadata']
        ))

        # Build PDF
        try:
            doc.build(elements)
            logger.info(f"Professional report generated: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise

    def _generate_kpis(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate KPI metrics from data.

        Args:
            df: Input DataFrame

        Returns:
            List of KPI dictionaries
        """
        kpis = []

        # Total records
        kpis.append({"label": "Total Records", "value": f"{len(df):,}"})

        # Numeric KPIs
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols[:4]:  # Limit to 4 KPIs
            total = df[col].sum()
            avg = df[col].mean()
            kpis.append({
                "label": f"{col.replace('_', ' ').title()} (Total)",
                "value": f"{total:,.2f}"
            })
            kpis.append({
                "label": f"{col.replace('_', ' ').title()} (Average)",
                "value": f"{avg:,.2f}"
            })

        return kpis[:8]  # Limit to 8 KPIs total

    def _create_kpi_table(self, kpis: List[Dict[str, Any]]) -> Table:
        """Create KPI table for report.

        Args:
            kpis: List of KPI dictionaries

        Returns:
            ReportLab Table object
        """
        # Create 2-column layout for KPIs
        data = []
        for i in range(0, len(kpis), 2):
            row = []
            for j in range(2):
                if i + j < len(kpis):
                    kpi = kpis[i + j]
                    row.extend([kpi['label'], kpi['value']])
                else:
                    row.extend(['', ''])
            data.append(row)

        table = Table(data, colWidths=[2.2*inch, 1.3*inch, 2.2*inch, 1.3*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica'),
            ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4a5568')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1a365d')),
            ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#4a5568')),
            ('TEXTCOLOR', (3, 0), (3, -1), colors.HexColor('#1a365d')),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f7fafc')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0'))
        ]))

        return table

    def _create_data_table(self, df: pd.DataFrame) -> Optional[Table]:
        """Create formatted data table.

        Args:
            df: Input DataFrame

        Returns:
            ReportLab Table object
        """
        if df.empty:
            return None

        # Prepare data
        data = [df.columns.tolist()]
        for _, row in df.iterrows():
            data.append([str(val)[:30] for val in row.values])  # Truncate long values

        # Calculate column widths
        num_cols = len(df.columns)
        col_width = 6.5 * inch / num_cols

        table = Table(data, colWidths=[col_width] * num_cols)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')])
        ]))

        return table
