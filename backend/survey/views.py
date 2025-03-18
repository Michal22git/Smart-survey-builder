from rest_framework import generics

from .models import Survey
from .serializers import SurveyListSerializer


class SurveyListAPIView(generics.ListAPIView):
    queryset = Survey.objects.all().order_by('-created_at')
    serializer_class = SurveyListSerializer
