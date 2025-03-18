from rest_framework import generics, status
from rest_framework.response import Response as DRFResponse

from .models import Survey
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
