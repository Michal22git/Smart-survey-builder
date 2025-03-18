from django.contrib import admin

from .models import Survey, Question, Option, Response, Answer


class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'public_id', 'response_count')
    readonly_fields = ('public_id', 'response_count')

admin.site.register(Survey, SurveyAdmin)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(Response)
admin.site.register(Answer)
