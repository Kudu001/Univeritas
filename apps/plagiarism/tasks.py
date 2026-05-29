from celery import shared_task


@shared_task(bind=True, max_retries=3)
def process_submission(self, version_id):
    try:
        from .services.pipeline import run_pipeline
        run_pipeline(version_id)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
