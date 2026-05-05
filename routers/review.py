from fastapi import APIRouter, Depends, status
from utils.auth import get_current_active_user
from fastapi import HTTPException
import models
from schema.review import CreateReview
from datetime import datetime
from utils.getdb import db_dependency
from sqlalchemy import func


router = APIRouter()


@router.post("/create-review")
def create_review(product_id: int, db: db_dependency, review: CreateReview,  current_user: models.User = Depends(get_current_active_user)):
    if current_user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    product = db.query(models.Product). filter(
        models.Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product does not exixts")

    purchased = db.query(models.OrderItem).join(models.Order, models.Order.id == models.OrderItem.order_id).filter(
        models.Order.customer_id == current_user.id, models.OrderItem.product_id == product_id, models.Order.status == "paid").first()

    if not purchased:
        raise HTTPException(
            status_code=400, detail="You can only review products you have purchased")

    new_review = models.Review(
        product_id=product_id,
        customer_id=current_user.id,
        rating=review.rating,
        comment=review.comment,
        created_at=datetime.utcnow()

    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return new_review


@router.get("/product_review/{product_id}")
def product_review(product_id: int, db: db_dependency):
    product = db.query(models.Product). filter(
        models.Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product does not exixts")

    all_review = db.query(models.Review).filter(
        models.Review.product_id == product_id).all()
    if not all_review:
        raise HTTPException(status_code=404, detail="No review")

    average_rating = db.query(func.avg(models.Review.rating)).filter(
        models.Review.product_id == product_id).scalar()

    total_review = db.query(func.count(models.Review.id)).filter(
        models.Review.product_id == product_id).scalar()

    return {
        "product_id": product_id,
        "total_review": total_review,
        "average_rating": average_rating if average_rating else 0,
        "reviews": all_review
    }
