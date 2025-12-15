from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.deps import require_user
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierOut

router = APIRouter(
    prefix="/api/suppliers",
    tags=["Suppliers"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=SupplierOut, status_code=status.HTTP_201_CREATED)
def create_supplier(
    payload: SupplierCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_user)
):
    if db.query(Supplier).filter(Supplier.name.ilike(payload.name)).first():
        raise HTTPException(status_code=400, detail="Supplier already exists")

    supplier = Supplier(name=payload.name)
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.get("/", response_model=list[SupplierOut])
def list_suppliers(
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user_id: int = Depends(require_user)
):
    query = db.query(Supplier)
    if search:
        query = query.filter(Supplier.name.ilike(f"%{search}%"))
    return query.all()


@router.put("/{supplier_id}", response_model=SupplierOut)
def update_supplier(
    supplier_id: int,
    payload: SupplierCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_user)
):
    supplier = db.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    supplier.name = payload.name
    db.commit()
    db.refresh(supplier)
    return supplier


@router.delete("/{supplier_id}")
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_user)
):
    supplier = db.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    db.delete(supplier)
    db.commit()
    return {"message": "Supplier deleted"}
