from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.deps import require_user
from app.models.sale import Sale
from app.models.product import Product
from app.schemas.sale import SaleCreate, SaleOut, SaleUpdate
router = APIRouter(
    prefix="/api/sales",
    tags=["Sales"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=SaleOut)
def create_sale(
    payload: SaleCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_user)
):
    product = db.get(Product, payload.product_id)
    if not product:
        raise HTTPException(404, "Product not found")

    if payload.quantity_sold > product.quantity:
        raise HTTPException(400, "Insufficient stock")

    product.quantity -= payload.quantity_sold

    sale = Sale(
        product_id=payload.product_id,
        quantity_sold=payload.quantity_sold
    )

    db.add(sale)
    db.commit()
    db.refresh(sale)

    return {
        "id": sale.id,
        "product_id": product.id,
        "product_name": product.name,
        "product_price": product.price,
        "quantity_sold": sale.quantity_sold,
        "created_at": sale.created_at,
    }


@router.get("/", response_model=list[SaleOut])
def list_sales(
    db: Session = Depends(get_db),
    user_id: int = Depends(require_user)
):
    sales = (
        db.query(Sale, Product)
        .join(Product, Sale.product_id == Product.id)
        .order_by(Sale.created_at.desc())
        .all()
    )

    result = []
    for sale, product in sales:
        result.append({
            "id": sale.id,
            "product_id": product.id,
            "product_name": product.name,
            "product_price": product.price,
            "quantity_sold": sale.quantity_sold,
            "created_at": sale.created_at,
        })

    return result


@router.put("/{sale_id}", response_model=SaleOut)
def update_sale(
    sale_id: int,
    payload: SaleCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_user)
):
    sale = db.get(Sale, sale_id)
    if not sale:
        raise HTTPException(404, "Sale not found")

    product = db.get(Product, payload.product_id)
    if not product:
        raise HTTPException(404, "Product not found")

    # restore previous stock
    old_product = db.get(Product, sale.product_id)
    old_product.quantity += sale.quantity_sold

    if payload.quantity_sold > product.quantity:
        raise HTTPException(400, "Insufficient stock")

    product.quantity -= payload.quantity_sold

    sale.product_id = payload.product_id
    sale.quantity_sold = payload.quantity_sold

    db.commit()
    db.refresh(sale)

    return sale  # ✅ matches SaleOut now

@router.delete("/{sale_id}")
def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_user)
):
    sale = db.get(Sale, sale_id)
    if not sale:
        raise HTTPException(404, "Sale not found")

    product = db.get(Product, sale.product_id)
    product.quantity += sale.quantity_sold  # restore stock

    db.delete(sale)
    db.commit()

    return {"message": "Sale deleted"}


