import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")
import seaborn as sns
import io
from typing import Dict, Any, Union
from wordcloud import WordCloud
import base64

from .schemas import ChartData


class SurveyVisualizer:
    """Class for creating visualizations from survey data."""

    def __init__(self, style: str = "whitegrid"):
        """Initialize the visualizer with a specified style."""
        self.style = style
        sns.set_style(self.style)

    def create_chart(self, chart_data: Union[ChartData, Dict[str, Any]]) -> str:
        """
        Create chart visualization based on chart data.

        Args:
            chart_data: ChartData model or dictionary with data for chart visualization

        Returns:
            Base64-encoded image string
        """
        if isinstance(chart_data, dict):
            chart_type = chart_data.get("type", "bar")
        else:
            chart_type = chart_data.type

        if chart_type == "bar":
            return self._create_bar_chart(chart_data)
        elif chart_type == "pie":
            return self._create_pie_chart(chart_data)
        elif chart_type in ["wordcloud", "word_cloud"]:
            return self._create_wordcloud(chart_data)
        else:

            return self._create_bar_chart(chart_data)

    def _create_bar_chart(self, chart_data: Union[ChartData, Dict[str, Any]]) -> str:
        """Create a bar chart visualization."""
        plt.figure(figsize=(10, 6))

        if isinstance(chart_data, dict):
            labels = chart_data.get("labels", [])
            values = chart_data.get("values", [])
            title = chart_data.get("title", "Responses")
        else:
            labels = chart_data.labels
            values = chart_data.values
            title = chart_data.title

        if not labels or not values:
            return self._get_empty_chart("No data available")

        sns.barplot(x=values, y=labels)
        plt.title(title)
        plt.xlabel("Number of responses")
        plt.tight_layout()

        return self._fig_to_base64()

    def _create_pie_chart(self, chart_data: Union[ChartData, Dict[str, Any]]) -> str:
        """Create a pie chart visualization."""
        plt.figure(figsize=(8, 8))

        if isinstance(chart_data, dict):
            labels = chart_data.get("labels", [])
            values = chart_data.get("values", [])
            title = chart_data.get("title", "Response Distribution")
        else:
            labels = chart_data.labels
            values = chart_data.values
            title = chart_data.title

        if not labels or not values:
            return self._get_empty_chart("No data available")

        plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
        plt.axis("equal")
        plt.title(title)
        plt.tight_layout()

        return self._fig_to_base64()

    def _create_wordcloud(self, chart_data: Union[ChartData, Dict[str, Any]]) -> str:
        """Create a word cloud visualization."""
        try:
            from wordcloud import WordCloud

            plt.figure(figsize=(10, 6))

            if isinstance(chart_data, dict):
                text_data = chart_data.get("text", "")
                title = chart_data.get("title", "Word Cloud")
            else:
                text_data = chart_data.text or ""
                title = chart_data.title

            if not text_data:
                return self._get_empty_chart("No text data available")

            wordcloud = WordCloud(
                width=800, height=400, background_color="white", max_words=100
            ).generate(text_data)

            plt.imshow(wordcloud, interpolation="bilinear")
            plt.axis("off")
            plt.title(title)
            plt.tight_layout()

            return self._fig_to_base64()
        except ImportError:
            return self._get_empty_chart("WordCloud package not installed")

    def _get_empty_chart(self, message: str) -> str:
        """Create an empty chart with a message."""
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, message, ha="center", va="center", fontsize=14)
        plt.axis("off")
        return self._fig_to_base64()

    def _fig_to_base64(self) -> str:
        """Convert matplotlib figure to base64 encoded string."""
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=100, bbox_inches="tight")
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        plt.close()
        return image_base64
