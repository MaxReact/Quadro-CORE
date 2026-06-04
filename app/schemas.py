from datetime import datetime

from pydantic import BaseModel


class AuthRequest(BaseModel):
    init_data: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    telegram_id: int
    name: str | None
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}
