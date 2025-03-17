from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/survey/generate/$", consumers.SurveyConsumer.as_asgi()),
]
