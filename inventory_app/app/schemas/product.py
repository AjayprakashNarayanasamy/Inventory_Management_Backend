from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2)
    sku: str = Field(..., min_length=2)
    price: int = Field(..., ge=0)
    quantity: int = Field(..., ge=0)
    category_id: int
    supplier_id: int


class ProductOut(BaseModel):
    id: int
    name: str
    sku: str
    price: int
    quantity: int
    category_id: int
    supplier_id: int

    model_config = {
        "from_attributes": True
    }
