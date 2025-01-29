from django.contrib import admin

from .models import Survey, Question, Option, Response, Answer

admin.site.register([Survey, Question, Option, Response, Answer])
