from pydantic import BaseModel


class CreateCart(BaseModel):
    product_id: int
    quantity: int

    class Config:
        from_attributes: True


class UpdateCart(BaseModel):
    quantity: int

    class Config:
        from_attributes: True
