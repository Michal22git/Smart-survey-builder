from rest_framework import serializers

from .models import Survey


class SurveyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ['id', 'title', 'description', 'created_at', 'public_id', 'response_count'] 