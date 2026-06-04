from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import User, UserRole
from app.schemas import AuthRequest, TokenResponse, UserResponse
from app.security import create_access_token, validate_init_data

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/telegram", response_model=TokenResponse)
def auth_telegram(body: AuthRequest, db: Session = Depends(get_db)) -> TokenResponse:
    tg_user = validate_init_data(body.init_data)

    telegram_id: int = tg_user["id"]
    name: str = tg_user.get("first_name", "") or tg_user.get("username", "")

    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if user is None:
        user = User(telegram_id=telegram_id, name=name, role=UserRole.admin)
        db.add(user)
    else:
        user.name = name

    db.commit()
    db.refresh(user)

    return TokenResponse(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
