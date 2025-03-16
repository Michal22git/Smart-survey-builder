import json
from typing import Optional, Iterator, Union

from .client import get_openai_client, get_default_model
from .exceptions import GenerationError, SchemaValidationError
from .prompts import (
    get_survey_system_prompt,
    get_question_regeneration_prompt,
    get_free_text_analysis_prompt
)
from .schemas import (
    SurveySchema,
    SurveyGenerationRequest,
    SurveyGenerationResponse,
    QuestionSchema,
    OptionSchema
)


class SurveyGenerator:
    """Generator for creating surveys using OpenAI."""
    
    def __init__(self, model: Optional[str] = None):
        """
        Initialize the survey generator.
        
        Args:
            model: Optional model name to use. If None, the default model will be used.
        """
        self.client = get_openai_client()
        self.model = model or get_default_model()

    def generate(self, request: SurveyGenerationRequest, stream: bool = False) -> Union[
        SurveyGenerationResponse, Iterator[str]]:
        """
        Generate a survey based on the provided request.

        Args:
            request: The survey generation request
            stream: Whether to stream the response

        Returns:
            If stream=False: A response containing the generated survey
            If stream=True: An iterator yielding response chunks

        Raises:
            GenerationError: If there's an error during generation
            SchemaValidationError: If the generated survey doesn't match the expected schema
        """
        try:
            system_prompt = get_survey_system_prompt(
                template=request.template,
                num_questions=request.num_questions,
                language=request.language
            )

            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Create a survey about: {request.prompt}"}
                ],
                stream=stream
            )

            if stream:
                return response

            content = response.choices[0].message.content
            survey_data = json.loads(content)
            survey = SurveySchema.model_validate(survey_data)

            return SurveyGenerationResponse(
                survey=survey,
                prompt=request.prompt,
                model=self.model
            )

        except json.JSONDecodeError as e:
            raise SchemaValidationError(f"Invalid JSON response from OpenAI: {str(e)}")
        except Exception as e:
            if "validation error" in str(e).lower():
                raise SchemaValidationError(f"Schema validation error: {str(e)}")
            else:
                raise GenerationError(f"Error generating survey: {str(e)}")

    def generate_from_free_text_stream(self, free_text: str) -> Iterator[Union[str, SurveyGenerationResponse]]:
        """
        Generate a survey based on free-form user description with streaming.

        Args:
            free_text: Free-form text describing the desired survey

        Returns:
            An iterator yielding response chunks and finally the complete survey

        Raises:
            GenerationError: If an error occurs during generation
            SchemaValidationError: If a schema validation error occurs
        """
        try:
            analysis_prompt = get_free_text_analysis_prompt()

            analysis_response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": analysis_prompt},
                    {"role": "user", "content": free_text}
                ]
            )

            content = analysis_response.choices[0].message.content
            params = json.loads(content)

            request = SurveyGenerationRequest(
                prompt=params.get("prompt", "Survey"),
                template=params.get("template", "general"),
                num_questions=params.get("num_questions", 5),
                language=params.get("language", "en")
            )

            yield {"type": "analysis_complete", "params": request.model_dump()}

            stream = self.generate(request, stream=True)
            for chunk in stream:
                yield {"type": "chunk",
                       "content": chunk.choices[0].delta.content if hasattr(chunk.choices[0], 'delta') and
                                                                    chunk.choices[0].delta.content else ""}

        except json.JSONDecodeError as e:
            yield {"type": "error", "message": f"Parameter analysis error: {str(e)}"}
        except Exception as e:
            yield {"type": "error", "message": f"Error generating survey: {str(e)}"}

    def process_stream(self, stream_iterator) -> SurveyGenerationResponse:
        """
        Process a stream of response chunks into a complete survey.

        Args:
            stream_iterator: Iterator yielding response chunks from OpenAI

        Returns:
            A complete survey generation response

        Raises:
            SchemaValidationError: If the generated survey doesn't match the expected schema
            GenerationError: If there's an error during generation
        """
        try:
            collected_content = ""
            for chunk in stream_iterator:
                if hasattr(chunk.choices[0], 'delta') and chunk.choices[0].delta.content:
                    collected_content += chunk.choices[0].delta.content
                    yield chunk.choices[0].delta.content

            survey_data = json.loads(collected_content)
            survey = SurveySchema.model_validate(survey_data)

            return SurveyGenerationResponse(
                survey=survey,
                prompt="",
                model=self.model
            )

        except json.JSONDecodeError as e:
            raise SchemaValidationError(f"Invalid JSON response from OpenAI: {str(e)}")
        except Exception as e:
            if "validation error" in str(e).lower():
                raise SchemaValidationError(f"Schema validation error: {str(e)}")
            else:
                raise GenerationError(f"Error generating survey: {str(e)}")
    
    def regenerate_question(self, survey_schema: SurveySchema, question_index: int, feedback: str = "") -> SurveySchema:
        """
        Regenerate a specific question in a survey schema before saving to database.
        
        Args:
            survey_schema: The survey schema containing all questions
            question_index: The index of the question to regenerate (0-based)
            feedback: Feedback on why the question should be regenerated
            
        Returns:
            Updated survey schema with the regenerated question
        
        Raises:
            GenerationError: If there's an error during regeneration
            ValueError: If the question index is invalid
        """
        try:
            if question_index < 0 or question_index >= len(survey_schema.questions):
                raise ValueError(f"Invalid question index: {question_index}. Survey has {len(survey_schema.questions)} questions.")

            question_to_regenerate = survey_schema.questions[question_index]

            other_questions = []
            for i, q in enumerate(survey_schema.questions):
                if i != question_index:
                    options_text = ""
                    if q.options:
                        options = [f"- {opt.text}" for opt in q.options]
                        options_text = "\nOptions:\n" + "\n".join(options)
                    
                    other_questions.append(f"Question {i+1}: {q.text} (Type: {q.type}){options_text}")

            question_data = {
                'text': question_to_regenerate.text,
                'type': question_to_regenerate.type,
                'required': question_to_regenerate.required
            }

            system_prompt = get_question_regeneration_prompt(
                survey_title=survey_schema.title,
                survey_description=survey_schema.description,
                other_questions=other_questions,
                question_to_regenerate=question_data,
                question_index=question_index,
                feedback=feedback
            )

            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt}
                ]
            )

            content = response.choices[0].message.content
            new_question_data = json.loads(content)
            
            new_options = None
            if "options" in new_question_data:
                new_options = [OptionSchema(text=opt["text"]) for opt in new_question_data["options"]]
            
            new_question = QuestionSchema(
                text=new_question_data["text"],
                type=new_question_data["type"],
                required=new_question_data.get("required", question_to_regenerate.required),
                options=new_options
            )

            updated_questions = survey_schema.questions.copy()
            updated_questions[question_index] = new_question

            updated_survey = SurveySchema(
                title=survey_schema.title,
                description=survey_schema.description,
                questions=updated_questions
            )
            
            return updated_survey
            
        except json.JSONDecodeError as e:
            raise SchemaValidationError(f"Invalid JSON response from OpenAI: {str(e)}")
        except ValueError as e:
            raise e
        except Exception as e:
            raise GenerationError(f"Error regenerating question: {str(e)}") 