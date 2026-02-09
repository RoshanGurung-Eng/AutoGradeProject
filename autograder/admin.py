from django.contrib import admin
from .models import TeacherQuestion

@admin.register(TeacherQuestion)
class TeacherQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_id', 'question_text', 'created_at')
    search_fields = ('question_id', 'question_text')
    list_filter = ('created_at',)