import logging

from celery import Celery

from src.settings import settings

logger = logging.getLogger("worker")
ch = logging.StreamHandler()

formatter = logging.Formatter(
    "[%(asctime)s][%(name)s][%(levelname)s]: %(message)s")

ch.setFormatter(formatter)

logger.addHandler(ch)

broker_url = (f"amqp://{settings.RABBITMQ_DEFAULT_USER}:{settings.RABBITMQ_DEFAULT_PASS}@rabbitmq:5672/"
              f"{settings.RABBITMQ_DEFAULT_VHOST}")
redis_url = "redis://redis"

queue = Celery("tasks", broker=broker_url, backend=redis_url)
queue.conf.timezone = "Europe/London"


@queue.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(5.0, test.s('hello'), name='add every 5')


@queue.task
def test(name: str):
    logger.critical("sas")
    return f"Hello {name}"
