# api/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import timedelta
from typing import List
from .auth import get_hashed_password, create_access_token, get_current_user, verify_password, User as AuthUser
from api.database import User as DBUser, Role  # Добавил импорт из api.database

router = APIRouter()
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class UserResponse(BaseModel):
    user_id: int
    login: str
    email: str
    first_name: str | None = None
    last_name: str | None = None
    role_id: int


@router.get("/users/", response_model=List[UserResponse])
async def list_users(current_user: AuthUser = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    users = list(DBUser.select())  # Изменил User на DBUser
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, current_user: AuthUser = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    try:
        user = DBUser.get(DBUser.user_id == user_id)  # Изменил User на DBUser
        return user
    except DBUser.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")


@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = None
    try:
        user = DBUser.get(DBUser.login == form_data.username)
    except DBUser.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})

    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.login, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
