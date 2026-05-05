from pydantic import BaseModel


class CreateCategory(BaseModel):
    name: str

    class Config:
        from_attributes = True
