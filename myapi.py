from fastapi import FastAPI
from routers.user import router as user_router
from routers.product import router as product_router
from routers.cart import router as cart_router
from routers.category import router as category_router
from routers.payment import router as payment_router
from routers.order import router as order_router
import models
from database import engine
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


"""
with engine.connect() as conn:
    conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    conn.execute(text("DROP TABLE IF EXISTS users"))
    conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
    conn.commit()

"""
load_dotenv()
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(user_router)
app.include_router(product_router)
app.include_router(cart_router)
app.include_router(category_router)
app.include_router(payment_router)
app.include_router(order_router)

# models.OrderItem.__table__.drop(engine)
# models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"""
@app.post("/token", response_model=Token)
async def create_token_login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):

    user = db.query(models.User).filter(
        models.User.username == form_data.username).first(
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")

    if not user.is_active:
        raise HTTPException(
            status_code=400, detail="Inactive User")

    access_token_expires = timedelta(minutes=TOKEN_EXPIRE)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

"""
