from fastapi import APIRouter, Depends, status
from schema.category import CreateCategory
from utils.auth import get_current_active_user
from fastapi import HTTPException
import models
from datetime import datetime
from utils.getdb import db_dependency

router = APIRouter()


@router.post("/create-category")
def create_category(category: CreateCategory, db: db_dependency, current_user: models.User = Depends(get_current_active_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    categories = models.Category(
        name=category.name
    )

    db.add(categories)
    db.commit()
    return {
        "successful!!"
    }


@router.get("/get-category")
def get_category(db: db_dependency):
    category = db.query(models.Category).filter(models.Category.name).all()

    return category
