#!/usr/bin/env python
"""
Test script to generate a survey report from the first available survey.
Run this from the Django project root.
"""

import os
import sys
from datetime import datetime

import django

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
project_dir = os.path.dirname(backend_dir)

sys.path.append(project_dir)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from survey.models import Survey, Response, Answer

from survey_analytics.report import ReportGenerator


def get_survey_data(survey):
    """Convert a Django Survey model to the dictionary format needed by ReportGenerator."""
    questions = survey.questions.all()
    print(f"Found {len(questions)} questions for survey ID: {survey.id}")

    question_list = []
    for q in questions:
        question_data = {
            "id": q.id,
            "text": q.text,
            "type": q.type,
            "required": q.required,
            "options": [],
        }

        if hasattr(q, "options"):
            for option in q.options.all():
                question_data["options"].append(
                    {"id": option.id, "text": option.text, "order": option.order}
                )

        question_list.append(question_data)

    schema = {"questions": question_list}

    return {
        "id": survey.id,
        "title": survey.title,
        "description": getattr(survey, "description", ""),
        "schema": schema,
        "public_id": getattr(survey, "public_id", str(survey.id)),
        "created_at": getattr(survey, "created_at", datetime.now()).isoformat(),
        "updated_at": (
            getattr(survey, "updated_at", None).isoformat()
            if getattr(survey, "updated_at", None)
            else None
        ),
    }


def get_response_data(response):
    """Convert a Django Response model to the dictionary format needed by ReportGenerator."""
    answers = Answer.objects.filter(response=response)
    print(f"Found {len(answers)} answers for response ID: {response.id}")

    formatted_answers = []
    for answer in answers:
        answer_data = {
            "id": answer.id,
            "question": answer.question_id,
            "text_answer": answer.text_answer or "",
        }

        if answer.selected_options.exists():
            answer_data["selected_options"] = [
                opt.id for opt in answer.selected_options.all()
            ]
        else:
            answer_data["selected_options"] = []

        formatted_answers.append(answer_data)

    return {
        "id": response.id,
        "survey_id": response.survey_id,
        "created_at": response.created_at.isoformat(),
        "respondent_name": response.respondent_name or "",
        "respondent_email": response.respondent_email or "",
        "answers": formatted_answers,
    }


def main():
    """Main function to generate and save a report."""
    print("Starting survey report generation...")

    surveys = Survey.objects.all()

    if not surveys:
        print("No surveys found in the database.")
        return

    for survey in surveys:
        responses = Response.objects.filter(survey=survey)
        if responses.exists():
            print(
                f"Using survey: {survey.title} (ID: {survey.id}) with {responses.count()} responses"
            )
            break
    else:
        print("No surveys with responses found.")
        return

    try:
        survey_data = get_survey_data(survey)
        responses_data = [get_response_data(response) for response in responses]
    except Exception as e:
        print(f"Error preparing data: {e}")
        import traceback

        traceback.print_exc()
        return

    print(
        f"Generating report for survey '{survey.title}' with {len(responses_data)} responses..."
    )

    report_generator = ReportGenerator(survey_data, responses_data)

    output_dir = os.path.join(project_dir, "survey_reports")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        pdf_report = report_generator.generate_report()
        pdf_path = os.path.join(output_dir, f"survey_{survey.id}_{timestamp}.pdf")
        with open(pdf_path, "wb") as pdf_file:
            pdf_file.write(pdf_report.getvalue())
        print(f"PDF report saved to: {pdf_path}")
    except Exception as e:
        print(f"Error generating PDF report: {e}")
        import traceback

        traceback.print_exc()

    print("\nReport generation complete!")
    print(f"Files are saved in the directory: {output_dir}")


if __name__ == "__main__":
    main()
