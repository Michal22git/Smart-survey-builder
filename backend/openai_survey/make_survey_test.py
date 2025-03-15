import json
import os
import sys

import django
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from openai_survey import SurveyGenerator, SurveySchema
from survey.models import Survey, Question, Option

load_dotenv()


def save_survey_to_database(survey_schema: SurveySchema, prompt: str) -> Survey:
    survey = Survey.objects.create(
        title=survey_schema.title,
        description=survey_schema.description or "",
        prompt=prompt
    )

    for i, q in enumerate(survey_schema.questions):
        question = Question.objects.create(
            survey=survey,
            text=q.text,
            type=q.type,
            required=q.required,
            order=i
        )

        if q.options:
            for j, opt in enumerate(q.options):
                Option.objects.create(
                    question=question,
                    text=opt.text,
                    order=j
                )

    return survey


def test_complete_survey_workflow():
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: OpenAI API key is missing. Set the OPENAI_API_KEY environment variable.")
        return

    free_text = input("\nDescribe the survey you want to create: ")
    generator = SurveyGenerator()

    try:
        print("\nGenerating survey based on the description...")

        response = generator.generate_from_free_text(free_text)
        survey_schema = response.survey

        print(f"\nGenerated survey: {survey_schema.title}")
        print(f"Description: {survey_schema.description}")
        print(f"Number of questions: {len(survey_schema.questions)}")
        print("\nQuestions:")

        for i, question in enumerate(survey_schema.questions, 1):
            print(f"\n{i}. {question.text} (type: {question.type}, required: {question.required})")
            if question.options:
                print("   Options:")
                for j, option in enumerate(question.options, 1):
                    print(f"   {j}. {option.text}")

        with open("generated_survey.json", "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, ensure_ascii=False, indent=2)
            print("\nSurvey saved to file 'generated_survey.json'")

        regenerate = input("\nDo you want to regenerate any question? (yes/no): ").lower()

        while regenerate == "yes":
            try:
                question_index = int(
                    input(f"Which question do you want to regenerate? (1-{len(survey_schema.questions)}): ")) - 1

                if question_index < 0 or question_index >= len(survey_schema.questions):
                    print(f"ERROR: Question index must be between 1 and {len(survey_schema.questions)}.")
                    continue

                feedback = input("Provide feedback on why this question should be changed: ")

                print("\nRegenerating question...")

                updated_survey = generator.regenerate_question(survey_schema, question_index, feedback)
                survey_schema = updated_survey

                print(f"\nUpdated survey: {survey_schema.title}")
                print("\nQuestions after regeneration:")

                for i, question in enumerate(survey_schema.questions, 1):
                    if i - 1 == question_index:
                        print(
                            f"\n{i}. [REGENERATED] {question.text} (type: {question.type}, required: {question.required})")
                    else:
                        print(f"\n{i}. {question.text} (type: {question.type}, required: {question.required})")

                    if question.options:
                        print("   Options:")
                        for j, option in enumerate(question.options, 1):
                            print(f"   {j}. {option.text}")

                with open("updated_survey.json", "w", encoding="utf-8") as f:
                    updated_data = {
                        "survey": survey_schema.model_dump(),
                        "prompt": free_text,
                        "model": response.model
                    }
                    json.dump(updated_data, f, ensure_ascii=False, indent=2)
                    print("\nUpdated survey saved to file 'updated_survey.json'")

                regenerate = input("\nDo you want to regenerate another question? (yes/no): ").lower()

            except ValueError as e:
                print(f"ERROR: {str(e)}")
                regenerate = input("\nDo you want to try again? (yes/no): ").lower()

        save_to_db = input("\nDo you want to save the survey to the database? (yes/no): ").lower() == 'yes'

        if save_to_db:
            survey = save_survey_to_database(survey_schema, free_text)
            print(f"\nSurvey saved to the database with ID: {survey.id}")
            print(f"Public ID: {survey.public_id}")
            print("\nQuestions saved in the database:")

            for i, question in enumerate(survey.questions.all(), 1):
                print(f"{i}. {question.text} (type: {question.type})")
                options = question.options.all()
                if options:
                    print("   Options:")
                    for j, option in enumerate(options, 1):
                        print(f"   {j}. {option.text}")
        else:
            print("\nSurvey was not saved to the database.")

    except Exception as e:
        print(f"ERROR: {str(e)}")


if __name__ == "__main__":
    print("=== COMPLETE SURVEY GENERATOR TEST ===")
    test_complete_survey_workflow()