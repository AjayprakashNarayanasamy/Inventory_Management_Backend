from pydantic import BaseModel, Field
from datetime import datetime


class SaleCreate(BaseModel):
    product_id: int
    quantity_sold: int = Field(..., gt=0)



class SaleOut(BaseModel):
    id: int
    product_id: int
    quantity_sold: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
class SaleUpdate(BaseModel):
    quantity_sold: int = Field(..., gt=0)
