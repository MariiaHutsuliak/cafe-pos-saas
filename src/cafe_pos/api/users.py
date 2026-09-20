from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from cafe_pos.database import get_db
from cafe_pos.models.user import User, UserRole
from cafe_pos.schemas.user import UserRead, UserUpdate
from cafe_pos.services.auth_service import get_current_user, require_role

router = APIRouter(tags=["users"])


@router.get("/admin/home")
def admin_home(current_user: User = Depends(require_role(UserRole.admin))):
    return {"message": f"Вітаємо в адмін-панелі, {current_user.email}"}


@router.get("/user/home")
def user_home(current_user: User = Depends(get_current_user)):
    return {"message": f"Вітаємо, {current_user.email}", "role": current_user.role}


@router.get("/users/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != UserRole.admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Немає доступу"
        )
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Не знайдено")
    return user


@router.put("/users/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Горизонтальне розмежування: user може редагувати тільки себе, admin — будь-кого
    if current_user.role != UserRole.admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Немає доступу"
        )

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Не знайдено")

    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    db.commit()
    db.refresh(user)
    return user
