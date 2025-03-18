from enum import Enum
from io import BytesIO
from typing import Dict, Any

from .analyzers import SurveyAnalyzer
from .exceptions import SurveyAnalyticsError
from .exporters import PDFExporter
from .schemas import SurveyAnalysisResult
from .visualizers import SurveyVisualizer


class ReportFormat(Enum):
    """Supported report format."""

    PDF = "pdf"


class ReportGenerator:
    """Main class for generating survey reports."""

    def __init__(self, survey_data: Dict[str, Any], responses: list):
        """
        Initialize the report generator.

        Args:
            survey_data: Dictionary with survey metadata and questions
            responses: List of response dictionaries
        """
        self.survey_data = survey_data
        self.responses = responses
        self.analyzer = SurveyAnalyzer(survey_data, responses)
        self.visualizer = SurveyVisualizer()
        self.analysis_result = None

    def generate_analysis(self) -> SurveyAnalysisResult:
        """
        Generate analysis of survey responses.

        Returns:
            Complete survey analysis result
        """
        if not self.analysis_result:
            self.analysis_result = self.analyzer.analyze()
        return self.analysis_result

    def add_visualizations(self) -> None:
        """
        Add visualizations to the analysis result.
        """
        if not self.analysis_result:
            self.generate_analysis()

        for question in self.analysis_result.questions:
            chart_image = self.visualizer.create_chart(question.chart_data)
            question.chart_image = chart_image

    def export_report(self, include_visualizations: bool = True) -> BytesIO:
        """
        Export analysis results to PDF format.

        Args:
            include_visualizations: Whether to include visualizations

        Returns:
            BytesIO object containing the PDF report
        """
        if not self.analysis_result:
            self.generate_analysis()

        if not self.analysis_result.questions:

            empty_buffer = BytesIO()
            empty_buffer.write(b"No questions found in survey")
            empty_buffer.seek(0)
            return empty_buffer

        if (
            include_visualizations
            and len(self.analysis_result.questions) > 0
            and not hasattr(self.analysis_result.questions[0], "chart_image")
        ):
            self.add_visualizations()

        exporter = PDFExporter(self.analysis_result)
        return exporter.export()

    def generate_report(self, include_visualizations: bool = True) -> BytesIO:
        """
        Generate a complete PDF report in one step.

        Args:
            include_visualizations: Whether to include visualizations

        Returns:
            BytesIO object containing the PDF report
        """
        try:

            self.generate_analysis()

            if include_visualizations:
                self.add_visualizations()

            return self.export_report(include_visualizations)
        except Exception as e:
            raise SurveyAnalyticsError(f"Failed to generate report: {str(e)}")

    @classmethod
    def from_survey_id(cls, survey_id: int, survey_service=None):
        """
        Create a report generator from a survey ID.

        Args:
            survey_id: ID of the survey
            survey_service: Service to fetch survey data and responses

        Returns:
            ReportGenerator instance
        """
        if survey_service is None:
            from survey.services import SurveyService

            survey_service = SurveyService()

        survey_data = survey_service.get_survey_by_id(survey_id)
        responses = survey_service.get_responses_for_survey(survey_id)

        return cls(survey_data, responses)
