"""
TaskLogger - A utility class for logging task execution status.

Usage in Celery tasks:
    from task_manager.logger import TaskLogger

    @shared_task(bind=True)
    def my_task(self):
        logger = TaskLogger(
            task_id=self.request.id,
            task_type="JOB_NIGHTLY_ETL"
        )
        
        logger.start()
        
        try:
            # ... do work ...
            logger.update(rows_processed=100)
            logger.success(rows_processed=500)
        except Exception as e:
            logger.failure(str(e))
            raise
"""

from django.utils import timezone
from .models import Job


class TaskLogger:
    """
    A reusable task logger that tracks task execution in the database.

    Attributes:
        task_id: The Celery task ID
        task_type: One of the JOB_TYPES defined in the Job model
        job: The Job model instance (created on start())
    """

    TASK_TYPES = {
        "JOB_NIGHTLY_ETL": "Job Nightly ETL",
        "JOB_MANUAL_ETL": "Job Manual ETL",
        "JOB_ML_TRAIN": "Job ML Training",
        "JOB_ML_PREDICT": "Job ML Prediction",
    }

    def __init__(self, task_id: str, task_type: str):
        """
        Initialize the TaskLogger.

        Args:
            task_id: The Celery task ID (self.request.id in a bound task)
            task_type: The type of job (must be one of TASK_TYPES keys)
        """
        if task_type not in self.TASK_TYPES:
            raise ValueError(
                f"Invalid task_type: {task_type}. Must be one of {list(self.TASK_TYPES.keys())}")

        self.task_id = task_id
        self.task_type = task_type
        self.job = None

    def start(self) -> "Job":
        """
        Create a new Job record and mark it as RUNNING.

        Returns:
            The created Job instance
        """
        self.job = Job.objects.create(
            celery_task_id=self.task_id,
            job_type=self.task_type,
            job_status="RUNNING",
        )
        return self.job

    def update(self, rows_processed: int = None, **kwargs) -> "Job":
        """
        Update the Job record with progress information.

        Args:
            rows_processed: Number of rows processed so far
            **kwargs: Additional fields to update

        Returns:
            The updated Job instance
        """
        if not self.job:
            raise RuntimeError(
                "TaskLogger.start() must be called before update()")

        if rows_processed is not None:
            self.job.rows_processed = rows_processed

        for key, value in kwargs.items():
            if hasattr(self.job, key):
                setattr(self.job, key, value)

        self.job.save()
        return self.job

    def success(self, rows_processed: int = None) -> "Job":
        """
        Mark the Job as SUCCESS and set the finished timestamp.

        Args:
            rows_processed: Final number of rows processed

        Returns:
            The updated Job instance
        """
        if not self.job:
            raise RuntimeError(
                "TaskLogger.start() must be called before success()")

        self.job.job_status = "SUCCESS"
        self.job.finished_at = timezone.now()

        if rows_processed is not None:
            self.job.rows_processed = rows_processed

        self.job.save()
        return self.job

    def failure(self, error_message: str) -> "Job":
        """
        Mark the Job as FAILED with an error message.

        Args:
            error_message: The error message to store

        Returns:
            The updated Job instance
        """
        if not self.job:
            # Create a job record even if start() wasn't called
            self.job = Job.objects.create(
                celery_task_id=self.task_id,
                job_type=self.task_type,
                job_status="FAILED",
                finished_at=timezone.now(),
                error_message=error_message,
            )
        else:
            self.job.job_status = "FAILED"
            self.job.finished_at = timezone.now()
            self.job.error_message = error_message
            self.job.save()

        return self.job

    def __enter__(self) -> "TaskLogger":
        """Context manager entry - starts the task."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Context manager exit - marks success or failure."""
        if exc_type is not None:
            self.failure(str(exc_val))
            return False  # Re-raise the exception
        self.success()
        return False
