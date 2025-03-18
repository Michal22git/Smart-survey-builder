from collections import Counter
from typing import List, Dict, Any

import pandas as pd

from .exceptions import AnalysisError
from .schemas import SurveyAnalysisResult, QuestionAnalysis, QuestionSummary, ChartData


class SurveyAnalyzer:
    """Analyzer for survey response data."""

    def __init__(self, survey_data: Dict[str, Any], responses: List[Dict[str, Any]]):
        """
        Initialize the analyzer with survey data and responses.

        Args:
            survey_data: Dictionary with survey metadata and questions
            responses: List of response dictionaries
        """
        self.survey_data = survey_data
        self.responses = responses
        self.df = self._prepare_dataframe()

    def _prepare_dataframe(self) -> pd.DataFrame:
        """Convert survey responses to a pandas DataFrame."""
        try:
            flattened_data = []
            for response in self.responses:
                response_base = {
                    "response_id": response["id"],
                    "respondent_name": response.get("respondent_name", ""),
                    "respondent_email": response.get("respondent_email", ""),
                    "submitted_at": response.get("created_at", None),
                }

                for answer in response.get("answers", []):
                    question_id = answer.get("question")
                    question_data = next(
                        (
                            q
                            for q in self.survey_data["schema"]["questions"]
                            if q["id"] == question_id
                        ),
                        None,
                    )

                    if not question_data:
                        continue

                    answer_row = response_base.copy()
                    answer_row.update(
                        {
                            "question_id": question_id,
                            "question_text": question_data.get("text", ""),
                            "question_type": question_data.get("type", ""),
                            "text_answer": answer.get("text_answer", ""),
                            "selected_options": answer.get("selected_options", []),
                        }
                    )
                    flattened_data.append(answer_row)

            return pd.DataFrame(flattened_data)
        except Exception as e:
            raise AnalysisError(f"Failed to prepare data frame: {str(e)}")

    def analyze(self) -> SurveyAnalysisResult:
        """
        Perform complete analysis of survey responses.

        Returns:
            A SurveyAnalysisResult object with all analysis data
        """
        try:
            total_responses = len(self.responses)

            if (
                "submitted_at" in self.df.columns
                and self.df["submitted_at"].notna().any()
            ):
                avg_time = "N/A"
            else:
                avg_time = None

            questions_analysis = []
            for question in self.survey_data["schema"]["questions"]:
                question_analysis = self._analyze_question(question)
                questions_analysis.append(question_analysis)

            completion_rate = 1.0

            return SurveyAnalysisResult(
                survey_id=self.survey_data["id"],
                survey_title=self.survey_data["title"],
                total_responses=total_responses,
                completion_rate=completion_rate,
                average_time_to_complete=avg_time,
                questions=questions_analysis,
            )
        except Exception as e:
            raise AnalysisError(f"Failed to analyze survey: {str(e)}")

    def _analyze_question(self, question: Dict[str, Any]) -> QuestionAnalysis:
        """
        Analyze responses for a specific question.

        Args:
            question: Question data dictionary

        Returns:
            QuestionAnalysis object with analysis results
        """
        question_id = question["id"]
        question_type = question["type"]
        question_df = self.df[self.df["question_id"] == question_id]

        response_count = len(question_df)

        if question_type == "text":
            return self._analyze_text_question(question, question_df)
        elif question_type in ["radio", "dropdown"]:
            return self._analyze_single_choice_question(question, question_df)
        elif question_type == "checkbox":
            return self._analyze_multiple_choice_question(question, question_df)
        else:
            summary = QuestionSummary(
                question_id=question_id,
                question_text=question["text"],
                question_type=question_type,
                response_count=response_count,
            )
            return QuestionAnalysis(
                summary=summary,
                chart_data={},
                insights="Question type not supported for detailed analysis.",
            )

    def _analyze_text_question(
        self, question: Dict[str, Any], question_df: pd.DataFrame
    ) -> QuestionAnalysis:
        """Analyze a text question."""
        question_id = question["id"]

        text_responses = question_df["text_answer"].dropna().tolist()
        text_responses = [t for t in text_responses if t.strip()]

        all_words = " ".join(text_responses).lower().split()
        word_counts = Counter(all_words)
        common_words = dict(word_counts.most_common(10))

        summary = QuestionSummary(
            question_id=question_id,
            question_text=question["text"],
            question_type=question["type"],
            response_count=len(question_df),
            text_responses=text_responses[:10],
        )

        all_text = " ".join(text_responses)
        chart_data = ChartData(type="wordcloud", title=question["text"], text=all_text)

        insight_text = f"Received {len(text_responses)} text responses. Most common words: {', '.join(list(common_words.keys())[:5])}"

        return QuestionAnalysis(
            summary=summary, chart_data=chart_data, insights=[insight_text]
        )

    def _analyze_single_choice_question(
        self, question: Dict[str, Any], question_df: pd.DataFrame
    ) -> QuestionAnalysis:
        """Analyze a single choice question (radio or dropdown)."""
        question_id = question["id"]

        option_map = {opt["id"]: opt["text"] for opt in question["options"]}

        option_counts = {}
        for option_id_list in question_df["selected_options"]:
            if not option_id_list:
                continue

            if len(option_id_list) > 0:
                option_id = option_id_list[0]
                option_text = option_map.get(option_id, f"Option {option_id}")
                option_counts[option_text] = option_counts.get(option_text, 0) + 1

        summary = QuestionSummary(
            question_id=question_id,
            question_text=question["text"],
            question_type=question["type"],
            response_count=len(question_df),
            option_counts=option_counts,
        )

        chart_data = ChartData(
            type="pie",
            title=question["text"],
            labels=list(option_counts.keys()),
            values=list(option_counts.values()),
        )

        most_popular = max(option_counts.items(), key=lambda x: x[1], default=(None, 0))
        insight_text = f"Most popular response: '{most_popular[0]}' ({most_popular[1]} responses, {most_popular[1]/len(question_df)*100:.1f}%)"

        return QuestionAnalysis(
            summary=summary, chart_data=chart_data, insights=[insight_text]
        )

    def _analyze_multiple_choice_question(
        self, question: Dict[str, Any], question_df: pd.DataFrame
    ) -> QuestionAnalysis:
        """Analyze a multiple choice question (checkbox)."""
        question_id = question["id"]

        option_map = {opt["id"]: opt["text"] for opt in question["options"]}

        option_counts = {opt["text"]: 0 for opt in question["options"]}

        for option_id_list in question_df["selected_options"]:
            if not option_id_list:
                continue

            for option_id in option_id_list:
                option_text = option_map.get(option_id, f"Option {option_id}")
                option_counts[option_text] = option_counts.get(option_text, 0) + 1

        summary = QuestionSummary(
            question_id=question_id,
            question_text=question["text"],
            question_type=question["type"],
            response_count=len(question_df),
            option_counts=option_counts,
        )

        chart_data = ChartData(
            type="bar",
            title=question["text"],
            labels=list(option_counts.keys()),
            values=list(option_counts.values()),
        )

        most_popular = max(option_counts.items(), key=lambda x: x[1], default=(None, 0))
        insight_text = f"Most selected option: '{most_popular[0]}' (selected {most_popular[1]} times)"

        return QuestionAnalysis(
            summary=summary, chart_data=chart_data, insights=[insight_text]
        )
