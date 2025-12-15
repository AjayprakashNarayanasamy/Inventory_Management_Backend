from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.deps import require_user
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryOut

router = APIRouter(
    prefix="/api/categories",
    tags=["Categories"]
)


# -------------------------
# DB DEPENDENCY
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# CREATE CATEGORY
# -------------------------
@router.post(
    "/",
    response_model=CategoryOut,
    status_code=status.HTTP_201_CREATED
)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_user)
):
    existing = db.query(Category).filter(
        Category.name.ilike(payload.name)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already exists"
        )

    category = Category(name=payload.name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


# -------------------------
# LIST + SEARCH CATEGORIES
# -------------------------
@router.get(
    "/",
    response_model=list[CategoryOut]
)
def list_categories(
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user_id: int = Depends(require_user)
):
    query = db.query(Category)

    if search:
        query = query.filter(
            Category.name.ilike(f"%{search}%")
        )

    return query.order_by(Category.id.desc()).all()


# -------------------------
# UPDATE CATEGORY
# -------------------------
@router.put(
    "/{category_id}",
    response_model=CategoryOut
)
def update_category(
    category_id: int,
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_user)
):
    category = db.get(Category, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    category.name = payload.name
    db.commit()
    db.refresh(category)
    return category


# -------------------------
# DELETE CATEGORY
# -------------------------
@router.delete(
    "/{category_id}",
    status_code=status.HTTP_200_OK
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_user)
):
    category = db.get(Category, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}
