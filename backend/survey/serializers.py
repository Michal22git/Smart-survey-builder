from rest_framework import serializers
from .models import Survey, Response, Answer, Option, Question


class SurveyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ['id', 'title', 'description', 'created_at', 'public_id', 'response_count']


class SurveyDetailSerializer(serializers.ModelSerializer):
    schema = serializers.SerializerMethodField()
    
    class Meta:
        model = Survey
        fields = ['id', 'title', 'description', 'created_at', 'public_id', 'schema']
    
    def get_schema(self, obj):
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
        
        return schema


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text']


class AnswerReadSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(read_only=True)
    selected_options = OptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Answer
        fields = ['question', 'text_answer', 'selected_options']


class AnswerCreateSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    selected_options = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        default=list
    )
    text_answer = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    
    class Meta:
        model = Answer
        fields = ['question', 'text_answer', 'selected_options']


class ResponseSerializer(serializers.ModelSerializer):
    answers = AnswerCreateSerializer(many=True, write_only=True)
    answer_details = AnswerReadSerializer(source='answers', many=True, read_only=True)
    
    class Meta:
        model = Response
        fields = ['id', 'respondent_name', 'respondent_email', 'answers', 'answer_details']
        read_only_fields = ['id', 'answer_details']
    
    def create(self, validated_data):
        answers_data = validated_data.pop('answers', [])
        response = Response.objects.create(**validated_data)
        
        for answer_data in answers_data:
            question = answer_data.pop('question')
            text_answer = answer_data.pop('text_answer', None)
            selected_options = answer_data.pop('selected_options', [])
            
            answer = Answer.objects.create(
                response=response,
                question=question,
                text_answer=text_answer
            )

            if selected_options:
                for option_id in selected_options:
                    try:
                        option = Option.objects.get(id=option_id)
                        answer.selected_options.add(option)
                    except Option.DoesNotExist:
                        print(f"Opcja o ID {option_id} nie istnieje")
        
        return response
        
    def update(self, instance, validated_data):
        answers_data = validated_data.pop('answers', [])

        instance.respondent_name = validated_data.get('respondent_name', instance.respondent_name)
        instance.respondent_email = validated_data.get('respondent_email', instance.respondent_email)
        instance.save()

        return instance


class SurveySerializer(serializers.ModelSerializer):
    
    response_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Survey
        fields = ['id', 'title', 'description', 'public_id', 'created_at', 'schema', 'response_count']
        read_only_fields = ['id', 'public_id', 'created_at']
    
    def get_response_count(self, obj):
        return obj.responses.count() 