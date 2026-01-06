from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from celery.result import AsyncResult

from .models import TaskRun
from .serializers import TaskRunSerializer
from .tasks import test_task, background_product_etl


class TaskManagerTestTask(APIView):
    """POST: Run a test task with optional duration parameter."""

    def post(self, request):
        duration = request.data.get('duration', 5)
        task = test_task.delay(duration)
        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)


class TaskManagerTaskStatus(APIView):
    """GET: Get the status of a Celery task by ID."""

    def get(self, request, task_id):
        task_result = AsyncResult(task_id)
        response = {
            "task_id": task_id,
            "status": task_result.status,
            "result": task_result.result if task_result.ready() else None
        }
        return Response(response, status=status.HTTP_200_OK)


class TaskManagerProductEtl(APIView):
    """POST: Trigger the background product ETL task."""

    def post(self, request):
        task = background_product_etl.delay(manual=True)
        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)


class TaskManagerRunList(APIView):
    """GET: List the most recent task runs."""

    def get(self, request):
        runs = TaskRun.objects.order_by("-created_at")[:50]
        return Response(TaskRunSerializer(runs, many=True).data)


class TaskManagerRunLatest(APIView):
    """GET: Get the most recent task run."""

    def get(self, request):
        run = TaskRun.objects.order_by("-created_at").first()
        if not run:
            return Response(None)
        return Response(TaskRunSerializer(run).data)
