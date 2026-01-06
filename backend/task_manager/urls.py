from django.urls import path
from .views import (
    TaskManagerTestTask,
    TaskManagerTaskStatus,
    TaskManagerProductEtl,
    TaskManagerRunList,
    TaskManagerRunLatest,
)

urlpatterns = [
    # Task execution endpoints
    path("task/test/", TaskManagerTestTask.as_view(), name="task-test"),
    path("task/status/<str:task_id>/",
         TaskManagerTaskStatus.as_view(), name="task-status"),
    path("task/product-etl/", TaskManagerProductEtl.as_view(),
         name="task-product-etl"),

    # Task run history endpoints
    path("task/runs/", TaskManagerRunList.as_view(), name="task-runs"),
    path("task/runs/latest/", TaskManagerRunLatest.as_view(),
         name="task-runs-latest"),
]
