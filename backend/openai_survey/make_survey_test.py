import json
import os
import sys
import time

import django
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from openai_survey import SurveyGenerator, SurveySchema, SurveyGenerationRequest
from survey.models import Survey, Question, Option

load_dotenv()


def save_survey_to_database(survey_schema: SurveySchema, prompt: str) -> Survey:
    survey = Survey.objects.create(
        title=survey_schema.title,
        description=survey_schema.description or "",
        prompt=prompt,
    )

    for i, q in enumerate(survey_schema.questions):
        question = Question.objects.create(
            survey=survey, text=q.text, type=q.type, required=q.required, order=i
        )

        if q.options:
            for j, opt in enumerate(q.options):
                Option.objects.create(question=question, text=opt.text, order=j)

    return survey


def test_complete_survey_workflow():
    if not os.environ.get("OPENAI_API_KEY"):
        print(
            "ERROR: OpenAI API key is missing. Set the OPENAI_API_KEY environment variable."
        )
        return

    free_text = input("\nDescribe the survey you want to create: ")
    generator = SurveyGenerator()

    try:
        print("\nGenerating survey with streaming...")
        print("=== REAL-TIME JSON STREAM ===")

        request = SurveyGenerationRequest(prompt=free_text)

        start_time = time.time()
        stream = generator.generate(request, stream=True)

        collected_content = ""
        for chunk in stream:
            if hasattr(chunk.choices[0], "delta") and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                collected_content += content
                print(content, end="", flush=True)

        print("\n\n=== STREAM COMPLETE ===")
        print(f"Generation time: {time.time() - start_time:.2f}s")

        try:
            survey_data = json.loads(collected_content)
            survey_schema = SurveySchema.model_validate(survey_data)
        except json.JSONDecodeError:
            print("\nERROR: Invalid JSON response")
            print("Raw content received:")
            print(collected_content)
            return

        print("\n=== GENERATED SURVEY ===")
        print(f"Title: {survey_schema.title}")
        print(f"Description: {survey_schema.description}")
        print(f"Number of questions: {len(survey_schema.questions)}")
        print("\nQuestions:")

        for i, question in enumerate(survey_schema.questions, 1):
            print(
                f"\n{i}. {question.text} (type: {question.type}, required: {question.required})"
            )
            if question.options:
                print("   Options:")
                for j, option in enumerate(question.options, 1):
                    print(f"   {j}. {option.text}")

        with open("generated_survey.json", "w", encoding="utf-8") as f:
            json.dump(survey_schema.model_dump(), f, ensure_ascii=False, indent=2)
            print("\nSurvey saved to 'generated_survey.json'")

        regenerate = input(
            "\nDo you want to regenerate any question? (yes/no): "
        ).lower()
        while regenerate == "yes":
            try:
                question_index = (
                    int(
                        input(
                            f"Which question do you want to regenerate? (1-{len(survey_schema.questions)}): "
                        )
                    )
                    - 1
                )

                if not 0 <= question_index < len(survey_schema.questions):
                    print(f"ERROR: Invalid question index")
                    continue

                feedback = input("Provide feedback for regeneration: ")

                print("\nRegenerating question...")
                updated_survey = generator.regenerate_question(
                    survey_schema, question_index, feedback
                )
                survey_schema = updated_survey

                print("\n=== UPDATED SURVEY ===")
                for i, q in enumerate(survey_schema.questions, 1):
                    prefix = "[REGENERATED] " if i - 1 == question_index else ""
                    print(f"\n{prefix}{i}. {q.text} ({q.type})")
                    if q.options:
                        print(
                            "   Options: " + ", ".join([opt.text for opt in q.options])
                        )

                with open("updated_survey.json", "w", encoding="utf-8") as f:
                    json.dump(
                        survey_schema.model_dump(), f, ensure_ascii=False, indent=2
                    )
                    print("\nUpdated survey saved to 'updated_survey.json'")

                regenerate = input("\nRegenerate another question? (yes/no): ").lower()

            except ValueError:
                print("Invalid input")
                regenerate = input("Try again? (yes/no): ").lower()

        if input("\nSave to database? (yes/no): ").lower() == "yes":
            survey = save_survey_to_database(survey_schema, free_text)

            for i, q in enumerate(survey.questions.all(), 1):
                print(f"{i}. {q.text}")
                if q.options.exists():
                    print(
                        "   Options: "
                        + ", ".join([opt.text for opt in q.options.all()])
                    )

    except Exception as e:
        print(f"\nERROR: {str(e)}")


if __name__ == "__main__":
    print("=== SURVEY GENERATOR WITH STREAMING ===")
    test_complete_survey_workflow()
