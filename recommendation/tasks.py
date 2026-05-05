import models
from database import SessionLocal
from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import RedisAsyncResultBackend
from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource

# Here's the broker that is going to execute tasks
broker = AioPikaBroker('amqp://guest:guest@localhost:5672').with_result_backend(
    RedisAsyncResultBackend("redis://localhost"))


# And here's the scheduler that is used to query scheduled sources
scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)


@broker.task(
    schedule=[
        {"cron": "0 17 * * *"}
    ]
)
async def fetch_product():
    db = SessionLocal()
    product = db.query(models.Product).all()
    db.close()
    print(f"Fetched {len(product)} products")
