"""Optional Celery task backend.

Activated by setting TASK_BACKEND=celery (with CELERY_BROKER_URL configured).
When TASK_BACKEND=local (default), FastAPI BackgroundTasks are used instead and
this module is never imported at runtime.
"""
try:
    from celery import Celery  # type: ignore
except ImportError:
    Celery = None  # type: ignore

from app.core.config import settings

if Celery is not None:
    celery_app = Celery(
        "exportguard",
        broker=settings.CELERY_BROKER_URL or "redis://localhost:6379/0",
        backend=settings.CELERY_BROKER_URL or "redis://localhost:6379/0",
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )

    @celery_app.task(name="process_document")
    def process_document_task_celery(document_id: str, shipment_id: str) -> None:
        import asyncio

        from app.tasks.process_document import process_document_task

        asyncio.run(process_document_task(document_id, shipment_id))

    @celery_app.task(name="run_analysis")
    def run_analysis_task_celery(shipment_id: str) -> None:
        import asyncio

        from app.tasks.process_document import run_analysis_task

        asyncio.run(run_analysis_task(shipment_id))
else:
    celery_app = None

    def process_document_task_celery(document_id: str, shipment_id: str) -> None:
        pass

    def run_analysis_task_celery(shipment_id: str) -> None:
        pass
