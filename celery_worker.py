from fork import create_app
from fork.celery_creator import celery
from fork.celery_utils import init_celery

app = create_app()
init_celery(celery, app)
