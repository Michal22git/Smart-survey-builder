from typing import Dict, Any

from django.db import transaction

from survey.models import Survey, Question, Option
from .schemas import SurveySchema, QuestionSchema


class SurveyProcessor:
    """Processor for OpenAI-generated surveys."""

    @staticmethod
    def schema_to_db_format(survey_schema: SurveySchema, prompt: str) -> Dict[str, Any]:
        """
        Convert a survey schema to a format suitable for database storage.

        Args:
            survey_schema: The survey schema to convert
            prompt: The original prompt used to generate the survey

        Returns:
            A dictionary with the survey data in a format ready for the database
        """
        return {
            "title": survey_schema.title,
            "description": survey_schema.description or "",
            "prompt": prompt,
            "questions": [
                SurveyProcessor._process_question(q, idx)
                for idx, q in enumerate(survey_schema.questions)
            ],
        }

    @staticmethod
    def _process_question(question: QuestionSchema, order: int) -> Dict[str, Any]:
        """
        Process a question schema into database format.

        Args:
            question: The question schema
            order: The order of the question in the survey

        Returns:
            A dictionary with the question data
        """
        question_data = {
            "text": question.text,
            "type": question.type,
            "required": question.required,
            "order": order,
            "options": [],
        }

        if question.options:
            question_data["options"] = [
                {"text": opt.text, "order": idx}
                for idx, opt in enumerate(question.options)
            ]

        return question_data

    @staticmethod
    @transaction.atomic
    def create_survey_from_schema(
        survey_schema: SurveySchema, prompt: str
    ) -> Dict[str, Any]:
        """
        Create a survey in the database from a schema.

        Args:
            survey_schema: The survey schema
            prompt: The original generation prompt

        Returns:
            The created survey data
        """
        survey_data = SurveyProcessor.schema_to_db_format(survey_schema, prompt)

        survey = Survey.objects.create(
            title=survey_data["title"],
            description=survey_data["description"],
            prompt=survey_data["prompt"],
        )

        for q_data in survey_data["questions"]:
            question = Question.objects.create(
                survey=survey,
                text=q_data["text"],
                type=q_data["type"],
                required=q_data["required"],
                order=q_data["order"],
            )

            for opt_data in q_data.get("options", []):
                Option.objects.create(
                    question=question, text=opt_data["text"], order=opt_data["order"]
                )

        return {
            "id": survey.id,
            "public_id": survey.public_id,
            "title": survey.title,
            "description": survey.description,
            "question_count": survey.questions.count(),
        }

    @staticmethod
    def analyze_survey_results(
        survey_id: int, max_responses: int = 100
    ) -> Dict[str, Any]:
        """
        Analyze the results of a survey.

        Args:
            survey_id: The ID of the survey to analyze
            max_responses: Maximum number of responses to analyze

        Returns:
            Analysis results
        """
        pass
