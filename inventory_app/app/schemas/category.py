from pydantic import BaseModel, Field


# Used when creating/updating category
class CategoryCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        example="Electronics"
    )


# Used when sending data back to client
class CategoryOut(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }

