from pydantic import BaseModel, Field


class SupplierCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)


class SupplierOut(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }
