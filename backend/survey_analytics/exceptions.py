class SurveyAnalyticsError(Exception):
    """Base exception for survey analytics module."""

    pass


class AnalysisError(SurveyAnalyticsError):
    """Error during survey data analysis."""

    pass


class VisualizationError(SurveyAnalyticsError):
    """Error during visualization generation."""

    pass


class ExportError(SurveyAnalyticsError):
    """Error during report export."""

    pass
