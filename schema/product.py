from pydantic import BaseModel
from typing import Optional


class CreateProduct(BaseModel):
    name: str
    description: str
    price: int
    stock: int
    category_id: Optional[int]

    class Config:
        from_attributes = True


class UpdateProduct(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    stock: Optional[int] = None
    category_id: Optional[int] = None

    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    product_img: str
    price: int
    stock: int

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    results: list[ProductResponse]
