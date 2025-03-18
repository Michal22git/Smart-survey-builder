from rest_framework import generics, status
from rest_framework.response import Response

from .models import Survey
from .serializers import SurveyListSerializer


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
            return Response({"message": "Survey was deleted."},
                          status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, 
                          status=status.HTTP_400_BAD_REQUEST)
