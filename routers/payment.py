from fastapi import APIRouter, Depends, HTTPException, status, Request
from utils.auth import get_current_active_user
import models
from utils.getdb import db_dependency
from config import settings
import requests
import hmac
import hashlib
import json
router = APIRouter()


@router.post("/initialize-payment")
def initialize_payment(db: db_dependency, current_user: models.User = Depends(get_current_active_user)):
    if current_user.role != "customer":
        raise HTTPException(
            status_code=401, detail="Unauthorized"
        )

    order = db.query(models.Order).filter(models.Order.customer_id == current_user.id,
                                          models.Order.status == "pending"
                                          ).first()
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT, detail="no pending order"
        )

    url = "https://api.paystack.co/transaction/initialize"

    data = {
        "email": current_user.email,
        "amount": int(order.total_amount * 100)

    }
    headers = {
        "authorization": f"Bearer {settings.PAYSTACK_TEST_SECRET_KEY}"

    }
    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()
    payment_link = response_data["data"]["authorization_url"]
    reference = response_data["data"]["reference"]

    order.payment_reference = reference
    db.commit()

    return {
        "payment_link": payment_link
    }


@router.post("/webhook")
async def webhook(request: Request, db: db_dependency):

    paystack_signature = request.headers.get('x-paystack-signature')
    body = await request.body()
    hash = hmac.new(
        settings.PAYSTACK_TEST_SECRET_KEY.encode('utf-8'),
        body,
        hashlib.sha512
    ).hexdigest()
    if hash != paystack_signature:
        raise HTTPException(status_code=401, detail="Invalid signature")

    parse_body = json.loads(body)
    event = parse_body.get("event")
    if event == "charge.success":
        reference = parse_body["data"]["reference"]

        orders = db.query(models.Order).filter(
            models.Order.payment_reference == reference).first()

        if not orders:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="does not exist "
            )
        orders.status = "paid"

        db.commit()

    return {
        "message": "OK"
    }
