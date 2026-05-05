from fastapi import APIRouter, Depends, status
from schema.cart import CreateCart, UpdateCart
from utils.auth import get_current_active_user
from fastapi import HTTPException
import models
from datetime import datetime
from utils.getdb import db_dependency

router = APIRouter()


@router.post("/create-cart")
def create_cart(cart: CreateCart, db: db_dependency, current_user: models.User = Depends(get_current_active_user)):
    if current_user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")

    product = db.query(models.Product).filter(models.Product.id == cart.product_id,
                                              models.Product.is_active == True).first()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product doesn't exist")

    if cart.quantity <= 0:
        raise HTTPException(
            status_code=400, detail="Quantity must be greater than 0")

    if cart.quantity > product.stock:
        raise HTTPException(
            status_code=400, detail="Quantity is more than the available stock")

    carts = db.query(models.Cart).filter(
        models.Cart.customer_id == current_user.id).first()
    if not carts:
        carts = models.Cart(
            customer_id=current_user.id,
            created_at=datetime.utcnow()
        )

    db.add(carts)
    db.commit()

    cart_item = models.CartItem(
        cart_id=carts.id,
        product_id=product.id,
        quantity=cart.quantity,
        price_at_time=product.price,
        updated_at=datetime.utcnow()
    )

    db.add(cart_item)

    db.commit()
    return {
        "message": "Carts updated successfully"
    }


@router.get("/view-cart")
def view_cart(db: db_dependency, current_user: models.User = Depends(get_current_active_user)):
    if current_user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")

    db_carts = db.query(models.CartItem).join(models.Cart, models.Cart.id ==
                                              models.CartItem.cart_id).filter(models.Cart.customer_id == current_user.id).all()

    total_amount = sum(item.quantity * item.price_at_time for item in db_carts)
    return {
        "items": db_carts,
        "Total": total_amount
    }


@router.patch("/update-quantity")
def update_quantity(cartitem_id: int, cart: UpdateCart, db: db_dependency, current_user: models.User = Depends(get_current_active_user)):
    if current_user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")

    db_carts = db.query(models.CartItem).join(models.Cart, models.Cart.id ==
                                              models.CartItem.cart_id).filter(models.Cart.customer_id == current_user.id,
                                                                              models.CartItem.id == cartitem_id).first()

    if cart.quantity is not None:
        db_carts.quantity = cart.quantity

    db.commit()
    return {
        "message": "Cart updated successfully"
    }


@router.delete("/delete-Item")
def delete_item(cartitem_id: int, db: db_dependency, current_user: models.User = Depends(get_current_active_user)):
    if current_user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")

    db_carts = db.query(models.CartItem).join(models.Cart, models.Cart.id ==
                                              models.CartItem.cart_id).filter(models.Cart.customer_id == current_user.id,
                                                                              models.CartItem.id == cartitem_id).first()
    if not db_carts:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_carts)
    db.commit()
    return {
        "Cart updated successfully"
    }


@router.post("/checkout")
def checkout(db: db_dependency, current_user: models.User = Depends(get_current_active_user)):
    if current_user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")

    db_carts = db.query(models.CartItem).join(models.Cart, models.Cart.id ==
                                              models.CartItem.cart_id).join(models.Product, models.Product.id == models.CartItem.product_id). filter(models.Cart.customer_id == current_user.id, models.Product.is_active == True).all()
    if not db_carts:
        raise HTTPException(status_code=404, detail="Cart Empty")
    total = 0
    for item in db_carts:
        product = db.query(models.Product).filter(
            models.Product.id == item.product_id).first()
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Item not available"
            )

        total += item.quantity * item.price_at_time

    order = models.Order(
        customer_id=current_user.id,
        total_amount=total,
        status="pending",
        created_at=datetime.utcnow()
    )

    db.add(order)
    db.commit()

    for item in db_carts:
        product = db.query(models.Product).filter(
            models.Product.id == item.product_id).first()
        order_item = models.OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_time=item.price_at_time
        )

        db.add(order_item)
        product.stock -= order_item.quantity
        db.commit()

    cart = db.query(models.Cart).filter(
        models.Cart.customer_id == current_user.id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    for item in db_carts:
        db.delete(item)
    db.commit()

    db.delete(cart)
    db.commit()
    return {
        "message": "Order Confirmed",
        "order id": order.id,
        "Total": order.total_amount
    }
