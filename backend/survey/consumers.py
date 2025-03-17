import asyncio
import json
from concurrent.futures import ThreadPoolExecutor

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from openai_survey import SurveyGenerator, SurveyGenerationRequest
from openai_survey.exceptions import GenerationError
from openai_survey.schemas import SurveySchema
from survey.models import Survey, Question, Option


class SurveyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(
            text_data=json.dumps(
                {
                    "type": "connection_established",
                    "message": "WebSocket connection established successfully.",
                }
            )
        )

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get("type", "")

            if message_type == "generate_survey":
                await self.handle_generate_survey(text_data_json)
            elif message_type == "regenerate_question":
                await self.handle_regenerate_question(text_data_json)
            elif message_type == "save_survey":
                await self.handle_save_survey(text_data_json)
            else:
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "error",
                            "message": f"Unknown message type: {message_type}",
                        }
                    )
                )

        except json.JSONDecodeError:
            await self.send(
                text_data=json.dumps(
                    {"type": "error", "message": "Invalid JSON format"}
                )
            )
        except Exception as e:
            await self.send(
                text_data=json.dumps(
                    {"type": "error", "message": f"An error occurred: {str(e)}"}
                )
            )

    async def handle_generate_survey(self, data):
        try:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "generation_started",
                        "message": "Survey generation started...",
                    }
                )
            )

            prompt = data.get("prompt", "")
            num_questions = data.get("num_questions", 5)
            template = data.get("template", "general")

            request = SurveyGenerationRequest(
                prompt=prompt, num_questions=num_questions, template=template
            )

            print(f"Generating survey with prompt: {prompt}")

            from openai_survey import get_openai_client

            generator = SurveyGenerator()

            if data.get("stream", True):
                response = await self.run_in_thread(
                    generator.generate, request=request, stream=True
                )

                collected_content = ""
                for chunk in response:
                    if (
                        hasattr(chunk.choices[0], "delta")
                        and chunk.choices[0].delta.content
                    ):
                        content = chunk.choices[0].delta.content
                        collected_content += content
                        await self.send(
                            text_data=json.dumps(
                                {"type": "generation_chunk", "content": content}
                            )
                        )

                try:
                    survey_data = json.loads(collected_content)

                    await self.send(
                        text_data=json.dumps(
                            {"type": "generation_complete", "survey": survey_data}
                        )
                    )
                except json.JSONDecodeError as e:
                    await self.send(
                        text_data=json.dumps(
                            {
                                "type": "error",
                                "message": f"Response parsing error: {str(e)}",
                            }
                        )
                    )
                    print(f"JSON parsing error: {e}")
                    print(f"Received content: {collected_content}")

            else:
                response = await self.run_in_thread(
                    generator.generate, request=request, stream=False
                )
                survey_data = response.survey.model_dump()

                await self.send(
                    text_data=json.dumps(
                        {"type": "generation_complete", "survey": survey_data}
                    )
                )
        except GenerationError as e:
            await self.send(
                text_data=json.dumps(
                    {"type": "error", "message": f"Generation error: {str(e)}"}
                )
            )
        except Exception as e:
            await self.send(
                text_data=json.dumps(
                    {"type": "error", "message": f"Unexpected error: {str(e)}"}
                )
            )

    async def handle_regenerate_question(self, data):
        try:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "regeneration_started",
                        "message": "Question regeneration started...",
                        "question_index": data.get("question_index"),
                    }
                )
            )

            survey_data = data.get("survey", {})
            question_index = data.get("question_index")
            feedback = data.get("feedback", "Please provide a better question")

            from openai_survey.schemas import SurveySchema

            survey_schema = SurveySchema.model_validate(survey_data)

            generator = SurveyGenerator()
            updated_survey = await self.run_in_thread(
                generator.regenerate_question,
                survey_schema=survey_schema,
                question_index=question_index,
                feedback=feedback,
            )

            await self.send(
                text_data=json.dumps(
                    {
                        "type": "regeneration_complete",
                        "survey": updated_survey.model_dump(),
                        "regenerated_index": question_index,
                    }
                )
            )

        except GenerationError as e:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "error",
                        "message": f"Question regeneration error: {str(e)}",
                    }
                )
            )
        except Exception as e:
            await self.send(
                text_data=json.dumps(
                    {"type": "error", "message": f"Unexpected error: {str(e)}"}
                )
            )

    def save_survey_to_database(
        self, survey_schema: SurveySchema, prompt: str
    ) -> Survey:
        """
        Save the generated survey to the database

        Args:
            survey_schema: The survey schema object
            prompt: The original prompt used to generate the survey

        Returns:
            The saved survey object
        """
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

    async def handle_save_survey(self, data):
        try:
            survey_data = data.get("survey", {})
            prompt = data.get("prompt", "")

            from openai_survey.schemas import SurveySchema

            survey_schema = SurveySchema.model_validate(survey_data)

            new_survey = await self.run_in_thread(
                self.save_survey_to_database, survey_schema=survey_schema, prompt=prompt
            )

            await self.send(
                text_data=json.dumps(
                    {
                        "type": "survey_saved",
                        "survey_data": {"id": new_survey.id, "title": new_survey.title},
                        "message": f'Survey "{new_survey.title}" has been saved successfully!',
                    }
                )
            )

        except Exception as e:
            import traceback

            traceback.print_exc()
            await self.send(
                text_data=json.dumps(
                    {"type": "error", "message": f"Error saving survey: {str(e)}"}
                )
            )

    async def run_in_thread(self, func, *args, **kwargs):
        with ThreadPoolExecutor() as pool:
            return await asyncio.get_event_loop().run_in_executor(
                pool, lambda: func(*args, **kwargs)
            )
