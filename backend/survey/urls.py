from django.urls import path

from .views import (
    SurveyListAPIView, 
    SurveyDeleteAPIView,
    SurveyDetailAPIView,
    SurveyResponseCreateAPIView
)

urlpatterns = [
    path('', SurveyListAPIView.as_view(), name='survey-list'),
    path('<str:public_id>/', SurveyDeleteAPIView.as_view(), name='survey-delete'),
    path('<str:public_id>/details/', SurveyDetailAPIView.as_view(), name='survey-detail'),
    path('<str:public_id>/respond/', SurveyResponseCreateAPIView.as_view(), name='survey-respond'),
]
