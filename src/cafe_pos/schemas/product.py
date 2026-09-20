from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    category: str
    price: float


class ProductRead(BaseModel):
    id: int
    name: str
    category: str
    price: float

    class Config:
        from_attributes = True
