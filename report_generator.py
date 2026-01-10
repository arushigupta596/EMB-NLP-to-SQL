"""Report generation module with charts and insights."""
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate detailed reports with charts and insights."""

    def __init__(self, output_dir: Path):
        """Initialize report generator.

        Args:
            output_dir: Directory to save generated reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Set up custom report styles."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        ))

        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            spaceAfter=12
        ))

    def generate_report(
        self,
        title: str,
        data_sections: List[Dict[str, Any]],
        charts: Optional[List[go.Figure]] = None,
        insights: Optional[List[str]] = None
    ) -> str:
        """Generate a comprehensive PDF report.

        Args:
            title: Report title
            data_sections: List of data sections, each containing 'title', 'data' (DataFrame), and optional 'description'
            charts: List of Plotly figures to include
            insights: List of insight text to include

        Returns:
            Path to the generated report
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.pdf"
        filepath = self.output_dir / filename

        # Create PDF document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Container for the 'Flowable' objects
        elements = []

        # Add title
        elements.append(Paragraph(title, self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.2 * inch))

        # Add generation timestamp
        timestamp_text = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        elements.append(Paragraph(timestamp_text, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.3 * inch))

        # Add insights section if provided
        if insights:
            elements.append(Paragraph("Key Insights", self.styles['CustomHeading']))
            for i, insight in enumerate(insights, 1):
                elements.append(Paragraph(f"{i}. {insight}", self.styles['CustomBody']))
            elements.append(Spacer(1, 0.2 * inch))

        # Add data sections
        for section in data_sections:
            section_title = section.get('title', 'Data Section')
            section_data = section.get('data')
            section_desc = section.get('description', '')

            elements.append(Paragraph(section_title, self.styles['CustomHeading']))

            if section_desc:
                elements.append(Paragraph(section_desc, self.styles['CustomBody']))
                elements.append(Spacer(1, 0.1 * inch))

            # Add data table
            if isinstance(section_data, pd.DataFrame) and not section_data.empty:
                table_data = self._dataframe_to_table(section_data)
                if table_data:
                    elements.append(table_data)
                    elements.append(Spacer(1, 0.2 * inch))

        # Add charts
        if charts:
            elements.append(PageBreak())
            elements.append(Paragraph("Visualizations", self.styles['CustomHeading']))
            elements.append(Spacer(1, 0.2 * inch))

            for i, fig in enumerate(charts):
                try:
                    # Convert Plotly figure to image
                    img_bytes = fig.to_image(format="png", width=600, height=400)
                    img = Image(io.BytesIO(img_bytes), width=5.5 * inch, height=3.67 * inch)
                    elements.append(img)
                    elements.append(Spacer(1, 0.3 * inch))

                    if i < len(charts) - 1:
                        elements.append(Spacer(1, 0.2 * inch))
                except Exception as e:
                    logger.error(f"Error adding chart {i}: {str(e)}")
                    elements.append(Paragraph(f"[Chart {i+1} could not be rendered]", self.styles['CustomBody']))

        # Build PDF
        try:
            doc.build(elements)
            logger.info(f"Report generated successfully: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise

    def _dataframe_to_table(self, df: pd.DataFrame, max_rows: int = 20) -> Optional[Table]:
        """Convert DataFrame to ReportLab Table.

        Args:
            df: Input DataFrame
            max_rows: Maximum number of rows to include

        Returns:
            ReportLab Table object
        """
        if df.empty:
            return None

        # Limit rows
        df_display = df.head(max_rows)

        # Prepare data
        data = [df_display.columns.tolist()]
        for _, row in df_display.iterrows():
            data.append([str(val)[:50] for val in row.values])  # Truncate long values

        # Create table
        table = Table(data)

        # Style table
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ])

        table.setStyle(style)
        return table

    def generate_quick_summary(
        self,
        df: pd.DataFrame,
        title: str = "Data Summary"
    ) -> Dict[str, Any]:
        """Generate a quick summary of a DataFrame.

        Args:
            df: Input DataFrame
            title: Summary title

        Returns:
            Dictionary containing summary statistics
        """
        summary = {
            'title': title,
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': df.columns.tolist(),
            'numeric_summary': {},
            'categorical_summary': {}
        }

        # Numeric columns summary
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            summary['numeric_summary'] = df[numeric_cols].describe().to_dict()

        # Categorical columns summary
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            summary['categorical_summary'][col] = {
                'unique_values': df[col].nunique(),
                'top_values': df[col].value_counts().head(5).to_dict()
            }

        return summary

    def generate_insights(self, df: pd.DataFrame, query_context: str = "") -> List[str]:
        """Generate automated insights from data.

        Args:
            df: Input DataFrame
            query_context: Context about the query

        Returns:
            List of insight strings
        """
        insights = []

        if df.empty:
            insights.append("No data available for analysis.")
            return insights

        # Row count insight
        insights.append(f"Dataset contains {len(df)} records with {len(df.columns)} columns.")

        # Numeric insights
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            if col in df.columns:
                mean_val = df[col].mean()
                max_val = df[col].max()
                min_val = df[col].min()
                insights.append(
                    f"{col.replace('_', ' ').title()}: "
                    f"Average = {mean_val:.2f}, "
                    f"Range = {min_val:.2f} to {max_val:.2f}"
                )

        # Categorical insights
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols[:3]:  # Limit to first 3 categorical columns
            unique_count = df[col].nunique()
            most_common = df[col].mode()[0] if len(df[col].mode()) > 0 else "N/A"
            insights.append(
                f"{col.replace('_', ' ').title()}: "
                f"{unique_count} unique values, "
                f"most common is '{most_common}'"
            )

        return insights[:10]  # Limit to 10 insights
