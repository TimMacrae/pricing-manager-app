from celery import shared_task
import time
import pandas as pd
from sqlalchemy import text
from .db import source_engine, analytics_engine
from .models import JobRun
from django.utils import timezone


@shared_task
def test_task(duration):
    """A simple test task that sleeps for a given duration."""
    time.sleep(duration)
    return f"-- Task test, slept for {duration} seconds"


@shared_task
def nightly_product_etl():
    # 1) Extract from source DB
    # query = text("""
    #     SELECT sku, name, price, cost, updated_at
    #     FROM products
    # """)
    # df = pd.read_sql(query, source_engine)

    # # 2) Transform
    # df["price"] = df["price"].astype(float)
    # df["cost"] = df["cost"].astype(float)

    # df["margin"] = df["price"] - df["cost"]
    # df["margin_pct"] = (df["margin"] / df["price"]).fillna(0.0)

    # # Example “business” features:
    # df["is_low_margin"] = df["margin_pct"] < 0.10
    # df["price_bucket"] = pd.cut(
    #     df["price"],
    #     bins=[0, 25, 50, 100, 200, 500, 1000, 10_000],
    #     include_lowest=True,
    # ).astype(str)

    # # 3) Load into analytics DB
    # # For learning: replace table each time
    # df.to_sql(
    #     "product_pricing_features",
    #     analytics_engine,
    #     if_exists="replace",
    #     index=False
    # )

    # return {"rows_written": int(len(df))}
    print("nightly_product_etl task called - not yet implemented")
    return {"status": "nightly_product_etl task is a placeholder and not yet implemented."}


@shared_task(bind=True)
def background_product_etl(self, manual: bool = False):
    job = JobRun.objects.create(
        job_type="JOB_MANUAL_ETL" if manual else "JOB_NIGHTLY_ETL",
        job_status="RUNNING",
        celery_task_id=self.request.id,
        started_at=timezone.now()
    )

    try:
        # Placeholder for actual ETL logic
        # 1) Extract
        # query = text("""
        #     SELECT sku, name, price, cost, updated_at
        #     FROM products
        # """)
        # df = pd.read_sql(query, source_engine)

        # # 2) Transform
        # df["price"] = df["price"].astype(float)
        # df["cost"] = df["cost"].astype(float)

        # df["margin"] = df["price"] - df["cost"]
        # df["margin_pct"] = (df["margin"] / df["price"]).fillna(0.0)

        # df["is_low_margin"] = df["margin_pct"] < 0.10

        # # 3) Load
        # df.to_sql(
        #     "product_pricing_features",
        #     analytics_engine,
        #     if_exists="replace",
        #     index=False
        # )

        # 4) Success
        job.status = "SUCCESS"
        job.rows_processed = 5  # len(df)
        job.finished_at = timezone.now()
        job.save()

        return {"rows_written": 5}
    except Exception as exc:
        job.job_status = "FAILED"
        job.error_message = str(exc)
        job.finished_at = timezone.now()
        job.save()
        raise
