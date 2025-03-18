import logging
import sys
import traceback

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views import View
from rest_framework import generics, status
from rest_framework.response import Response as DRFResponse

from survey_analytics.report import ReportGenerator
from .models import Survey, Response, Answer
from .serializers import (
    SurveyListSerializer,
    SurveyDetailSerializer,
    ResponseSerializer
)

class SurveyListAPIView(generics.ListAPIView):
    queryset = Survey.objects.all().order_by('-created_at')
    serializer_class = SurveyListSerializer


class SurveyDeleteAPIView(generics.DestroyAPIView):
    serializer_class = SurveyListSerializer
    lookup_field = 'public_id'
    
    def get_queryset(self):
        return Survey.objects.all()

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return DRFResponse({"message": "Survey was deleted."},
                          status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return DRFResponse({"error": str(e)}, 
                          status=status.HTTP_400_BAD_REQUEST)


class SurveyDetailAPIView(generics.RetrieveAPIView):
    serializer_class = SurveyDetailSerializer
    lookup_field = 'public_id'
    
    def get_queryset(self):
        return Survey.objects.all()
    
    def get_object(self):
        obj = super().get_object()
        print(f"Pobrano ankietę: {obj.title} z ID: {obj.public_id}")

        schema = {
            'questions': []
        }
        
        questions = obj.questions.all().prefetch_related('options')
        for question in questions:
            question_data = {
                'id': question.id,
                'text': question.text,
                'type': question.type,
                'required': question.required,
                'options': []
            }
            
            if question.type in ['radio', 'checkbox', 'dropdown']:
                for option in question.options.all():
                    question_data['options'].append({
                        'id': option.id,
                        'text': option.text
                    })
            
            schema['questions'].append(question_data)
        
        obj.schema = schema
        return obj


class SurveyResponseCreateAPIView(generics.CreateAPIView):
    serializer_class = ResponseSerializer
    
    def create(self, request, *args, **kwargs):
        public_id = self.kwargs.get('public_id')
        try:
            survey = Survey.objects.get(public_id=public_id)
        except Survey.DoesNotExist:
            return DRFResponse(
                {"detail": "Ankieta nie istnieje."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(survey=survey)

        response_obj = serializer.save(survey=survey)
        print(f"Zapisano odpowiedź: {response_obj.id} dla ankiety: {survey.title}")
        print(f"Liczba odpowiedzi dla tej ankiety: {survey.responses.count()}")
        
        return DRFResponse(serializer.data, status=status.HTTP_201_CREATED)


class SurveyReportView(View):
    def get(self, request, public_id):
        try:
            survey = get_object_or_404(Survey, public_id=public_id)
            print(f"[DEBUG] Znaleziono ankietę: {survey.title} (ID: {survey.id})")
            responses = Response.objects.filter(survey=survey)
            
            if not responses.exists():
                return HttpResponse("Cant generate report", status=400)

            survey_data = self.prepare_survey_data(survey)
            responses_data = [self.prepare_response_data(response) for response in responses]

            generator = ReportGenerator(survey_data, responses_data)
            pdf_buffer = generator.generate_report(include_visualizations=True)
            filename = f"survey_report_{survey.public_id}.pdf"
            
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            print(f"[ERROR] Error while generating report: {str(e)}")
            traceback.print_exc(file=sys.stdout)
            return HttpResponse(f"Error while generating report: {str(e)}", status=500)
    
    def prepare_survey_data(self, survey):
        questions = survey.questions.all()
        question_list = []
        for q in questions:
            question_data = {
                "id": q.id,
                "text": q.text,
                "type": q.type,
                "required": q.required,
                "options": []
            }

            if hasattr(q, 'options'):
                for option in q.options.all():
                    question_data["options"].append({
                        "id": option.id,
                        "text": option.text,
                        "order": getattr(option, 'order', 0)
                    })
            
            question_list.append(question_data)
        
        schema = {"questions": question_list}
        
        return {
            "id": survey.id,
            "title": survey.title,
            "description": getattr(survey, 'description', ''),
            "schema": schema,
            "public_id": survey.public_id,
            "created_at": survey.created_at.isoformat(),
            "updated_at": survey.updated_at.isoformat() if survey.updated_at else None
        }
    
    def prepare_response_data(self, response):
        answers = Answer.objects.filter(response=response)
        
        formatted_answers = []
        for answer in answers:
            answer_data = {
                "id": answer.id,
                "question": answer.question_id,
                "text_answer": answer.text_answer or ""
            }

            if hasattr(answer, 'selected_options') and answer.selected_options.exists():
                answer_data["selected_options"] = [opt.id for opt in answer.selected_options.all()]
            else:
                answer_data["selected_options"] = []
                
            formatted_answers.append(answer_data)
        
        return {
            "id": response.id,
            "survey_id": response.survey_id,
            "created_at": response.created_at.isoformat(),
            "respondent_name": response.respondent_name or "",
            "respondent_email": response.respondent_email or "",
            "answers": formatted_answers
        }
