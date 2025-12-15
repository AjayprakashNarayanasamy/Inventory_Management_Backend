from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.deps import require_user
from app.models.product import Product
from app.models.category import Category
from app.models.supplier import Supplier
from app.schemas.product import ProductCreate, ProductOut

router = APIRouter(
    prefix="/api/products",
    tags=["Products"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=ProductOut)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_user)
):
    # Validate FK
    if not db.get(Category, payload.category_id):
        raise HTTPException(400, "Invalid category")

    if not db.get(Supplier, payload.supplier_id):
        raise HTTPException(400, "Invalid supplier")

    if db.query(Product).filter(Product.sku == payload.sku).first():
        raise HTTPException(400, "SKU already exists")

    product = Product(**payload.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/", response_model=list[ProductOut])
def list_products(
    search: str | None = Query(default=None),
    category_id: int | None = None,
    supplier_id: int | None = None,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_user)
):
    query = db.query(Product)

    if search:
        query = query.filter(
            (Product.name.ilike(f"%{search}%")) |
            (Product.sku.ilike(f"%{search}%"))
        )

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if supplier_id:
        query = query.filter(Product.supplier_id == supplier_id)

    return query.order_by(Product.id.desc()).all()


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    payload: ProductCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_user)
):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")

    for key, value in payload.dict().items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_user)
):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")

    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}
