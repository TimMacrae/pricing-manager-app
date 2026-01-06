from django.urls import path
from .views import get_task, run_task, post_background_product_etl, list_jobs, latest_job

urlpatterns = [
    path("task", run_task, name="task"),
    path("task/<str:task_id>", get_task, name="task_status"),
    path("task/background-product-etl", post_background_product_etl,
         name="background_product_etl"),
    path("jobs/", list_jobs),
    path("jobs/latest/", latest_job),
]
