from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import JobRun
from .serializers import JobRunSerializer
from .tasks import test_task, background_product_etl
from celery.result import AsyncResult


# Create your views here.


@api_view(['POST'])
def run_task(request):
    print("Received request to run test task", request.data)
    duration = request.data.get('duration', 5)  # default to 5 seconds
    task = test_task.delay(duration)
    return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)


@api_view(['GET'])
def get_task(request, task_id):
    task_result = AsyncResult(task_id)
    response = {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None
    }
    return Response(response, status=status.HTTP_200_OK)


@api_view(['POST'])
def post_background_product_etl(request):
    task = background_product_etl.delay(manual=True)
    return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)


@api_view(["GET"])
def list_jobs(request):
    jobs = JobRun.objects.order_by("-created_at")[:50]
    return Response(JobRunSerializer(jobs, many=True).data)


@api_view(["GET"])
def latest_job(request):
    job = JobRun.objects.order_by("-created_at").first()
    if not job:
        return Response(None)
    return Response(JobRunSerializer(job).data)
