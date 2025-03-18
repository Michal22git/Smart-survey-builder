from datetime import datetime
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field


class RespondentInfo(BaseModel):
    """Information about a survey respondent."""

    name: Optional[str] = None
    email: Optional[str] = None
    responded_at: datetime


class AnswerData(BaseModel):
    """Data for a single answer."""

    question_id: int
    question_text: str
    question_type: str
    text_answer: Optional[str] = None
    selected_options: Optional[List[Dict[str, Any]]] = None


class ResponseData(BaseModel):
    """Data for a single survey response."""

    response_id: int
    respondent: RespondentInfo
    answers: List[AnswerData]


class QuestionSummary(BaseModel):
    """Summary statistics for a survey question."""

    question_id: int
    question_text: str
    question_type: str
    response_count: int
    text_responses: Optional[List[str]] = None
    option_counts: Optional[Dict[str, int]] = None


class ChartData(BaseModel):
    """Data for chart visualization."""

    type: str
    title: str
    labels: List[str] = []
    values: List[int] = []
    text: Optional[str] = None


class QuestionAnalysis(BaseModel):
    """Complete analysis for a single question."""

    summary: QuestionSummary
    chart_data: ChartData
    insights: List[str] = []
    chart_image: Optional[str] = None


class SurveyAnalysisResult(BaseModel):
    """Complete analysis result for a survey."""

    survey_id: int
    survey_title: str
    total_responses: int
    completion_rate: float
    average_time_to_complete: Optional[str] = None
    questions: List[QuestionAnalysis] = []
    created_at: datetime = Field(default_factory=datetime.now)
