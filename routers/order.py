from fastapi import APIRouter, Depends, status
from utils.auth import get_current_active_user
from fastapi import HTTPException
import models
from utils.getdb import db_dependency
router = APIRouter()


@router.get("/orders/pending")
def all_orders(db: db_dependency, current_user: models.User = Depends(get_current_active_user)):
    if current_user.role != "customer":
        raise HTTPException(
            status_code=401, detail="Unauthorized"
        )

    all_order = db.query(models.Order).filter(
        models.Order.customer_id == current_user.id, models.Order.status == "pending").first()

    if not all_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No order pending"
        )
    return all_order


@router.get("/all_order/admin")
def orders(db: db_dependency, current_user: models.User = Depends(get_current_active_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=401, detail="Unauthorized"
        )
    orders = db.query(models.Order).all()
    if not orders:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No orders"
        )

    return orders


@router.get("/all_order")
def orders(db: db_dependency, current_user: models.User = Depends(get_current_active_user)):
    if current_user.role != "customer":
        raise HTTPException(
            status_code=401, detail="Unauthorized"
        )
    orders = db.query(models.Order).filter(
        models.Order.customer_id == current_user.id).all()
    if not orders:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No orders"
        )

    return orders


@router.get("/orders/{order_id}")
def orders(order_id: int, db: db_dependency, current_user: models.User = Depends(get_current_active_user)):
    if current_user.role != "customer":
        raise HTTPException(
            status_code=401, detail="Unauthorized"
        )

    order = db.query(models.Order).filter(
        models.Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )
    items = db.query(models.OrderItem).filter(
        models.OrderItem.order_id == order_id
    ).all()

    if not items:
        raise HTTPException(status_code=404, detail="Cart Empty")
    return {
        "order_id": order.id,
        "status": order.status,
        "items": items
    }


@router.get("/orders/{order_id}")
def orders(order_id: int, db: db_dependency, current_user: models.User = Depends(get_current_active_user)):

    order = db.query(models.Order).filter(
        models.Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )
    if current_user.role == "customer" and order.customer_id != current_user:
        raise HTTPException(
            status_code=401, detail="Unauthorized"
        )

    items = db.query(models.OrderItem).filter(
        models.OrderItem.order_id == order_id
    ).all()

    if not items:
        raise HTTPException(status_code=404, detail="Cart Empty")
    return {
        "order_id": order.id,
        "status": order.status,
        "items": items
    }


@router.patch("/orders/{order_id}/shipped")
def shipped_orders(order_id: int, db: db_dependency, current_user: models.User = Depends(get_current_active_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=401, detail="Unauthorized"
        )
    all_order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.status == "pending").first()

    if not all_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No order pending"
        )

    all_order.status = "shipped"

    db.commit()
    db.refresh(all_order)
    return {
        "message":  "Order updated successfully",
        "order_id": all_order.id,
        "status": all_order.status
    }


@router.patch("/orders/{order_id}/out_for_delivery")
def out_for_delivery(order_id: int, db: db_dependency, current_user: models.User = Depends(get_current_active_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=401, detail="Unauthorized"
        )
    all_order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.status == "shipped").first()

    if not all_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No order shipped"
        )

    all_order.status = "out_for_delivery"

    db.commit()
    db.refresh(all_order)
    return {
        "message":  "Order updated successfully",
        "order_id": all_order.id,
        "status": all_order.status
    }


@router.patch("/orders/{order_id}/delivered")
def delivered(order_id: int, db: db_dependency, current_user: models.User = Depends(get_current_active_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=401, detail="Unauthorized"
        )
    all_order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.status == "out_for_delivery").first()

    if not all_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No order out for delivery"
        )

    all_order.status = "delivered"

    db.commit()
    db.refresh(all_order)
    return {
        "message":  "Order updated successfully",
        "order_id": all_order.id,
        "status": all_order.status
    }


@router.patch("/orders/{order_id}/cancel")
def cancel_order(order_id: int, db: db_dependency, current_user: models.User = Depends(get_current_active_user)):
    if current_user.role != "customer":
        raise HTTPException(
            status_code=401, detail="Unauthorized"
        )

    all_order = db.query(models.Order).filter(
        models.Order.customer_id == current_user.id,
        models.Order.id == order_id).first()

    if not all_order:
        raise HTTPException(
            status_code=400, detail="No order found"
        )

    if all_order.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Order can't be cancelled"
        )

    all_order.status = "cancelled"

    db.commit()
    db.refresh(all_order)
    return {
        "message": "Order Cancelled",
        "order_id": all_order.id,
        "status": all_order.status
    }
