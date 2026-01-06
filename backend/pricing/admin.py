from django.contrib import admin
from .models import JobRun

# Register your models here.


@admin.register(JobRun)
class JobRunAdmin(admin.ModelAdmin):
    list_display = ('id', 'job_type', 'job_status',
                    'started_at', 'finished_at', 'rows_processed')
    list_filter = ('job_type', 'job_status', 'started_at', 'finished_at')
    search_fields = ('celery_task_id', 'error_message')
