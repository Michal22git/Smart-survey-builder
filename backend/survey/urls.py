from django.urls import path

from .views import SurveyListAPIView, SurveyDeleteAPIView

urlpatterns = [
    path('', SurveyListAPIView.as_view(), name='survey-list'),
    path('<str:public_id>/', SurveyDeleteAPIView.as_view(), name='survey-delete'),
]
