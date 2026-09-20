from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from cafe_pos.database import get_db
from cafe_pos.models.product import Product
from cafe_pos.models.user import User, UserRole
from cafe_pos.schemas.product import ProductCreate, ProductRead
from cafe_pos.services.auth_service import get_current_user, require_role

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductRead])
def list_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # будь-яка роль, аби залогінений
):
    return db.query(Product).all()


@router.post("/", response_model=ProductRead, status_code=201)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),  # тільки admin
):
    product = Product(**product_in.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
