from fastapi import FastAPI
from database import engine
import models
from router.recommendation import router as recommendation_router
models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(recommendation_router)
