"""Chart and visualization generation module."""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class ChartGenerator:
    """Generate charts and visualizations from data."""

    def __init__(self, theme: str = "plotly_white"):
        """Initialize chart generator.

        Args:
            theme: Plotly theme to use
        """
        self.theme = theme
        self.default_colors = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A"]

    def generate_chart(
        self,
        df: pd.DataFrame,
        chart_type: str,
        x_col: Optional[str] = None,
        y_col: Optional[str] = None,
        title: Optional[str] = None,
        **kwargs
    ) -> go.Figure:
        """Generate a chart based on the specified type.

        Args:
            df: DataFrame containing the data
            chart_type: Type of chart ('bar', 'line', 'pie', 'scatter', etc.)
            x_col: Column for x-axis
            y_col: Column for y-axis
            title: Chart title
            **kwargs: Additional chart-specific parameters

        Returns:
            Plotly Figure object
        """
        if df.empty:
            return self._create_empty_chart("No data available")

        # Auto-detect columns if not provided
        if x_col is None and len(df.columns) > 0:
            x_col = df.columns[0]
        if y_col is None and len(df.columns) > 1:
            y_col = df.columns[1]

        chart_methods = {
            'bar': self._create_bar_chart,
            'line': self._create_line_chart,
            'pie': self._create_pie_chart,
            'scatter': self._create_scatter_chart,
            'histogram': self._create_histogram,
            'box': self._create_box_plot,
            'heatmap': self._create_heatmap
        }

        method = chart_methods.get(chart_type, self._create_bar_chart)

        try:
            fig = method(df, x_col, y_col, title, **kwargs)
            fig.update_layout(template=self.theme)
            return fig
        except Exception as e:
            logger.error(f"Error creating {chart_type} chart: {str(e)}")
            return self._create_empty_chart(f"Error creating chart: {str(e)}")

    def _create_bar_chart(
        self,
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: Optional[str] = None,
        **kwargs
    ) -> go.Figure:
        """Create a bar chart."""
        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            title=title or f"{y_col} by {x_col}",
            color_discrete_sequence=self.default_colors,
            **kwargs
        )
        fig.update_layout(
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title(),
        )
        return fig

    def _create_line_chart(
        self,
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: Optional[str] = None,
        **kwargs
    ) -> go.Figure:
        """Create a line chart."""
        fig = px.line(
            df,
            x=x_col,
            y=y_col,
            title=title or f"{y_col} over {x_col}",
            color_discrete_sequence=self.default_colors,
            **kwargs
        )
        fig.update_layout(
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title(),
        )
        return fig

    def _create_pie_chart(
        self,
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: Optional[str] = None,
        **kwargs
    ) -> go.Figure:
        """Create a pie chart."""
        fig = px.pie(
            df,
            names=x_col,
            values=y_col,
            title=title or f"Distribution of {y_col}",
            color_discrete_sequence=self.default_colors,
            **kwargs
        )
        return fig

    def _create_scatter_chart(
        self,
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: Optional[str] = None,
        **kwargs
    ) -> go.Figure:
        """Create a scatter plot."""
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            title=title or f"{y_col} vs {x_col}",
            color_discrete_sequence=self.default_colors,
            **kwargs
        )
        fig.update_layout(
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title(),
        )
        return fig

    def _create_histogram(
        self,
        df: pd.DataFrame,
        x_col: str,
        y_col: Optional[str] = None,
        title: Optional[str] = None,
        **kwargs
    ) -> go.Figure:
        """Create a histogram."""
        fig = px.histogram(
            df,
            x=x_col,
            title=title or f"Distribution of {x_col}",
            color_discrete_sequence=self.default_colors,
            **kwargs
        )
        fig.update_layout(
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title="Count",
        )
        return fig

    def _create_box_plot(
        self,
        df: pd.DataFrame,
        x_col: Optional[str] = None,
        y_col: str = None,
        title: Optional[str] = None,
        **kwargs
    ) -> go.Figure:
        """Create a box plot."""
        fig = px.box(
            df,
            x=x_col,
            y=y_col,
            title=title or f"Box Plot of {y_col}",
            color_discrete_sequence=self.default_colors,
            **kwargs
        )
        return fig

    def _create_heatmap(
        self,
        df: pd.DataFrame,
        x_col: Optional[str] = None,
        y_col: Optional[str] = None,
        title: Optional[str] = None,
        **kwargs
    ) -> go.Figure:
        """Create a heatmap."""
        # For heatmap, use correlation matrix if not specified
        if df.select_dtypes(include=['number']).shape[1] > 1:
            corr_matrix = df.select_dtypes(include=['number']).corr()
            fig = px.imshow(
                corr_matrix,
                title=title or "Correlation Heatmap",
                color_continuous_scale='RdBu_r',
                aspect='auto',
                **kwargs
            )
        else:
            return self._create_empty_chart("Not enough numeric columns for heatmap")

        return fig

    def _create_empty_chart(self, message: str) -> go.Figure:
        """Create an empty chart with a message."""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False)
        )
        return fig

    def auto_generate_chart(self, df: pd.DataFrame, question: str = "") -> go.Figure:
        """Automatically generate the best chart based on data characteristics.

        Args:
            df: DataFrame containing the data
            question: Optional question to help determine chart type

        Returns:
            Plotly Figure object
        """
        if df.empty:
            return self._create_empty_chart("No data available")

        # Determine chart type based on data characteristics
        num_rows = len(df)
        num_cols = len(df.columns)
        numeric_cols = df.select_dtypes(include=['number']).columns
        categorical_cols = df.select_dtypes(include=['object']).columns

        # Small dataset with one categorical and one numeric column -> bar chart
        if num_rows <= 20 and len(categorical_cols) > 0 and len(numeric_cols) > 0:
            return self._create_bar_chart(df, categorical_cols[0], numeric_cols[0])

        # Two numeric columns -> scatter plot
        elif len(numeric_cols) >= 2:
            return self._create_scatter_chart(df, numeric_cols[0], numeric_cols[1])

        # Single numeric column -> histogram
        elif len(numeric_cols) == 1:
            return self._create_histogram(df, numeric_cols[0])

        # Time series data -> line chart
        elif any('date' in col.lower() for col in df.columns):
            date_col = [col for col in df.columns if 'date' in col.lower()][0]
            if len(numeric_cols) > 0:
                return self._create_line_chart(df, date_col, numeric_cols[0])

        # Default to bar chart
        return self._create_bar_chart(df, df.columns[0], df.columns[1] if num_cols > 1 else df.columns[0])
