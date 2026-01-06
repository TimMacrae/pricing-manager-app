from django.db import models

# Create your models here.


class JobRun(models.Model):
    JOB_TYPES = [
        ("JOB_NIGHTLY_ETL", "Job Nightly ETL"),
        ("JOB_MANUAL_ETL", "Job Manual ETL"),
        ("JOB_ML_TRAIN", "Job ML Training"),
        ("JOB_ML_PREDICT", "Job ML Prediction"),
    ]

    JOB_STATUS = [
        ("PENDING", "Pending"),
        ("RUNNING", "Running"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    celery_task_id = models.CharField(max_length=255, blank=True, null=True)
    job_type = models.CharField(max_length=50, choices=JOB_TYPES)
    job_status = models.CharField(
        max_length=20, choices=JOB_STATUS, default="PENDING")
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    rows_processed = models.IntegerField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"JobRun {self.job_type} [{self.job_status}] - {self.created_at:%Y-%m-%d %H:%M:%S}"
