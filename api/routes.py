from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import timedelta
from typing import List, Optional
from .auth import get_hashed_password, create_access_token, get_current_user, verify_password, User as AuthUser
# Добавил импорт моделей
from api.database import User as DBUser, Role, Component, Category, Manufacturer, User

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


# Pydantic models for User
class UserBase(BaseModel):
    login: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: str  # Добавляем поле пароля
    role_id: int


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    user_id: int

    class Config:
        from_attributes = True


# User-related routes (unchanged)
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
    print(f"Attempting login for user: {form_data.username}")
    user = None
    try:
        user = DBUser.get(DBUser.login == form_data.username)
        print(
            f"User found: {user.login}, role_id: {user.role.role_id}, role_name: {user.role.role_name}")
    except DBUser.DoesNotExist:
        print(f"User not found: {form_data.username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})

    if not verify_password(form_data.password, user.password):
        print("Incorrect password")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.login, expires_delta=access_token_expires
    )

    # Добавляем информацию о пользователе в ответ
    print("Successful authentication")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "username": user.login,
        "role_id": user.role.role_id,
        "role_name": user.role.role_name  # Добавляем роль пользователя в ответ
    }


# User CRUD routes (доступны только для администраторов)
@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, current_user: AuthUser = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    try:
        hashed_password = get_hashed_password(user.password)  # Хешируем пароль
        db_user = User.create(
            login=user.login,
            password=hashed_password,  # Сохраняем хешированный пароль
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role_id
        )
        return db_user
    except IntegrityError:
        raise HTTPException(
            status_code=400, detail="Login or email already exists")


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserCreate, current_user: AuthUser = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    try:
        # Corrected User to DBUser
        db_user = DBUser.get(DBUser.user_id == user_id)
        hashed_password = get_hashed_password(user.password)  # Хешируем пароль
        db_user.login = user.login
        db_user.password = hashed_password  # Сохраняем хешированный пароль
        db_user.email = user.email
        db_user.first_name = user.first_name
        db_user.last_name = user.last_name
        db_user.role = user.role_id
        db_user.save()
        return db_user
    except DBUser.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    except IntegrityError:
        raise HTTPException(
            status_code=400, detail="Login or email already exists")


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, current_user: AuthUser = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    try:
        # Corrected User to DBUser
        db_user = DBUser.get(DBUser.user_id == user_id)
        db_user.delete_instance()
        return
    except DBUser.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")


# Pydantic models for Role
class RoleBase(BaseModel):
    role_name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleResponse(RoleBase):
    role_id: int

    class Config:
        from_attributes = True


# Role CRUD routes (доступны только для администраторов)
@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(role: RoleCreate, current_user: AuthUser = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    try:
        db_role = Role.create(role_name=role.role_name,
                              description=role.description)
        return db_role
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Role name already exists")


@router.get("/roles", response_model=List[RoleResponse])
async def list_roles(current_user: AuthUser = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    roles = list(Role.select())
    return roles


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(role_id: int, current_user: AuthUser = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    try:
        role = Role.get(Role.role_id == role_id)
        return role
    except Role.DoesNotExist:
        raise HTTPException(status_code=404, detail="Role not found")


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(role_id: int, role: RoleCreate, current_user: AuthUser = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    try:
        db_role = Role.get(Role.role_id == role_id)
        db_role.role_name = role.role_name
        db_role.description = role.description
        db_role.save()
        return db_role
    except Role.DoesNotExist:
        raise HTTPException(status_code=404, detail="Role not found")
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Role name already exists")


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: int, current_user: AuthUser = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    try:
        role = Role.get(Role.role_id == role_id)
        role.delete_instance()
        return
    except Role.DoesNotExist:
        raise HTTPException(status_code=404, detail="Role not found")


# Component CRUD routes
@router.post("/components", response_model=ComponentResponse, status_code=status.HTTP_201_CREATED)
async def create_component(component: ComponentCreate, current_user: AuthUser = Depends(get_current_user)):
    # Разрешаем доступ всем аутентифицированным пользователям
    # if current_user.role not in ("admin", "staff"):
    #    raise HTTPException(status_code=403, detail="Insufficient privileges")
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
    # Разрешаем доступ всем аутентифицированным пользователям
    # if current_user.role not in ("admin", "staff"):
    #    raise HTTPException(status_code=403, detail="Insufficient privileges")
    components = list(Component.select())
    return components


@router.get("/components/{component_id}", response_model=ComponentResponse)
async def get_component(component_id: int, current_user: AuthUser = Depends(get_current_user)):
    # Разрешаем доступ всем аутентифицированным пользователям
    # if current_user.role not in ("admin", "staff"):
    #    raise HTTPException(status_code=403, detail="Insufficient privileges")
    try:
        component = Component.get(Component.component_id == component_id)
        return component
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Component not found")


@router.put("/components/{component_id}", response_model=ComponentResponse)
async def update_component(component_id: int, component: ComponentCreate, current_user: AuthUser = Depends(get_current_user)):
    # Разрешаем доступ всем аутентифицированным пользователям
    # if current_user.role not in ("admin", "staff"):
    #    raise HTTPException(status_code=403, detail="Insufficient privileges")
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
    # Разрешаем доступ всем аутентифицированным пользователям
    # if current_user.role not in ("admin", "staff"):
    #    raise HTTPException(status_code=403, detail="Insufficient privileges")
    try:
        component = Component.get(Component.component_id == component_id)
        component.delete_instance()
        return
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Component not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
