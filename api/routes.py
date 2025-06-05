# api/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import timedelta
from typing import List, Optional
from .auth import get_hashed_password, create_access_token, get_current_user, verify_password, User as AuthUser
# Добавил импорт моделей
from api.database import User as DBUser, Role, Component, Category, Manufacturer
from peewee import DoesNotExist, IntegrityError

router = APIRouter()
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Pydantic models (serializers) for components


class CategoryBase(BaseModel):
    category_name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    category_id: int

    class Config:
        from_attributes = True


class ManufacturerBase(BaseModel):
    manufacturer_name: str
    contact_information: Optional[str] = None


class ManufacturerCreate(ManufacturerBase):
    pass


class ManufacturerResponse(ManufacturerBase):
    manufacturer_id: int

    class Config:
        from_attributes = True


class ComponentBase(BaseModel):
    component_name: str
    description: Optional[str] = None
    category_id: int
    manufacturer_id: int
    price: float
    quantity_in_stock: int


class ComponentCreate(ComponentBase):
    pass


class ComponentResponse(BaseModel):
    component_id: int
    component_name: str
    description: Optional[str] = None
    category_id: int
    manufacturer_id: int
    price: float
    quantity_in_stock: int

    class Config:
        from_attributes = True


# User-related routes (unchanged)
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
    users = list(DBUser.select())  # Changed User to DBUser
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, current_user: AuthUser = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    try:
        user = DBUser.get(DBUser.user_id == user_id)  # Changed User to DBUser
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

# Component CRUD routes


@router.post("/components", response_model=ComponentResponse, status_code=status.HTTP_201_CREATED)
async def create_component(component: ComponentCreate, current_user: AuthUser = Depends(get_current_user)):
    if current_user.role not in ("admin", "staff"):
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    try:
        # Retrieve Category and Manufacturer objects
        category = Category.get(Category.category_id == component.category_id)
        manufacturer = Manufacturer.get(
            Manufacturer.manufacturer_id == component.manufacturer_id)

        # Create the component
        db_component = Component.create(
            component_name=component.component_name,
            description=component.description,
            category=category,
            manufacturer=manufacturer,
            price=component.price,
            quantity_in_stock=component.quantity_in_stock
        )
        return db_component
    except DoesNotExist:
        raise HTTPException(
            status_code=400, detail="Invalid category_id or manufacturer_id")
    except IntegrityError:
        raise HTTPException(
            status_code=400, detail="Integrity error: Check data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/components", response_model=List[ComponentResponse])
async def list_components(current_user: AuthUser = Depends(get_current_user)):
    if current_user.role not in ("admin", "staff"):
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    components = list(Component.select())
    return components


@router.get("/components/{component_id}", response_model=ComponentResponse)
async def get_component(component_id: int, current_user: AuthUser = Depends(get_current_user)):
    if current_user.role not in ("admin", "staff"):
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    try:
        component = Component.get(Component.component_id == component_id)
        return component
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Component not found")


@router.put("/components/{component_id}", response_model=ComponentResponse)
async def update_component(component_id: int, component: ComponentCreate, current_user: AuthUser = Depends(get_current_user)):
    if current_user.role not in ("admin", "staff"):
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    try:
        db_component = Component.get(Component.component_id == component_id)

        # Retrieve Category and Manufacturer objects
        category = Category.get(Category.category_id == component.category_id)
        manufacturer = Manufacturer.get(
            Manufacturer.manufacturer_id == component.manufacturer_id)

        db_component.component_name = component.component_name
        db_component.description = component.description
        db_component.category = category
        db_component.manufacturer = manufacturer
        db_component.price = component.price
        db_component.quantity_in_stock = component.quantity_in_stock
        db_component.save()
        return db_component
    except DoesNotExist:
        raise HTTPException(
            status_code=404, detail="Component not found or invalid category/manufacturer IDs")
    except IntegrityError:
        raise HTTPException(
            status_code=400, detail="Integrity error: Check data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/components/{component_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_component(component_id: int, current_user: AuthUser = Depends(get_current_user)):
    if current_user.role not in ("admin", "staff"):
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    try:
        component = Component.get(Component.component_id == component_id)
        component.delete_instance()
        return
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Component not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
