from django.urls import path

from .views import (
    SurveyListAPIView, 
    SurveyDeleteAPIView,
    SurveyDetailAPIView,
    SurveyResponseCreateAPIView,
    SurveyReportView
)

urlpatterns = [
    path('', SurveyListAPIView.as_view(), name='survey-list'),
    path('<str:public_id>/', SurveyDeleteAPIView.as_view(), name='survey-delete'),
    path('<str:public_id>/details/', SurveyDetailAPIView.as_view(), name='survey-detail'),
    path('<str:public_id>/respond/', SurveyResponseCreateAPIView.as_view(), name='survey-respond'),
    path('<str:public_id>/report/', SurveyReportView.as_view(), name='survey-report'),
]
