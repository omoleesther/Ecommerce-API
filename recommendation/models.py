from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, DECIMAL
from database import Base
from datetime import datetime, timezone


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(200), nullable=False, unique=True)
    email = Column(String(200), nullable=False, unique=True)
    phone = Column(String(30), nullable=True)
    role = Column(String(20), nullable=False)
    password_hash = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    join_date = Column(DateTime(timezone=True),
                       default=lambda: datetime.now(timezone.utc))
    confirmed = Column(Boolean, default=False)


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    description = Column(String(240), nullable=False)
    price = Column(DECIMAL(12, 2), nullable=False)
    stock = Column(Integer, nullable=False)
    product_img = Column(String(200), nullable=False,
                         default="productDefault.jpg")
    owner_id = Column(Integer, ForeignKey('users.id'))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True),
                        default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)


class Cart(Base):
    __tablename__ = 'carts'

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True),
                        default=lambda: datetime.now(timezone.utc))


class CartItem(Base):
    __tablename__ = 'cart_items'

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey('carts.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
    price_at_time = Column(DECIMAL(12, 2), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('users.id'))
    total_amount = Column(DECIMAL(12, 2), nullable=False)
    status = Column(String(30), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)
    payment_reference = Column(String(100), nullable=True)


class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
    price_at_time = Column(DECIMAL(12, 2), nullable=False)


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    customer_id = Column(Integer, ForeignKey('users.id'))
    rating = Column(Integer, nullable=False)
    comment = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.utcnow)
