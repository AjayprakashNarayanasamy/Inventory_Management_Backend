from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import pandas as pd

from app.core.database import SessionLocal
from app.core.deps import require_user
from app.models.product import Product
from app.models.category import Category
from app.models.supplier import Supplier
from app.models.sale import Sale

router = APIRouter(
    prefix="/api/reports",
    tags=["Reports"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/inventory")
def inventory_report(
    db: Session = Depends(get_db),
    user_id: int = Depends(require_user)
):
    query = (
        db.query(
            Product.id,
            Product.name,
            Product.sku,
            Product.price,
            Product.quantity,
            Category.name.label("category"),
            Supplier.name.label("supplier")
        )
        .join(Category, Product.category_id == Category.id)
        .join(Supplier, Product.supplier_id == Supplier.id)
    )

    df = pd.DataFrame(query.all())

    return {
        "count": len(df),
        "data": df.to_dict(orient="records")
    }


@router.get("/sales")
def sales_report(
    db: Session = Depends(get_db),
    user_id: int = Depends(require_user)
):
    query = (
        db.query(
            Sale.id,
            Sale.product_id,
            Sale.quantity_sold,
            Sale.created_at
        )
    )

    df = pd.DataFrame(query.all())

    return {
        "count": len(df),
        "data": df.to_dict(orient="records")
    }
