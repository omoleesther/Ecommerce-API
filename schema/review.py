from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CreateReview(BaseModel):
    rating: int
    comment: str

    class Config:
        from_attributes = True
