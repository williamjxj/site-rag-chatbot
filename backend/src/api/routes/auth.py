"""Authentication routes - mounted under /api/auth/*.
Adapted from https://github.com/jxjwilliam/python-nextjs-agent
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ...auth import create_access_token, decode_token, hash_password, verify_password
from ...db import User, get_db
from ...schemas import (
    LoginRequest,
    LoginResponse,
    UserCreate,
    UserProfileUpdate,
    UserRegistrationResponse,
    UserResponse,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)
) -> User:
    """Dependency to validate JWT token."""
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/register", response_model=UserRegistrationResponse, status_code=201)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    existing = (
        db.query(User)
        .filter((User.email == user_data.email) | (User.username == user_data.username))
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Email or username already registered")

    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
    )
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="User already exists")

    return UserRegistrationResponse(user=new_user)


@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT."""
    user = db.query(User).filter(User.username == login_data.username).first()

    if not user or not verify_password(login_data.password, str(user.hashed_password)):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is disabled")

    access_token = create_access_token(data={"sub": str(user.id)})
    return LoginResponse(access_token=access_token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user profile."""
    if profile_data.email and profile_data.email != current_user.email:
        if db.query(User).filter(User.email == profile_data.email).first():
            raise HTTPException(status_code=409, detail="Email already registered")
        current_user.email = profile_data.email
    if profile_data.full_name is not None:
        current_user.full_name = profile_data.full_name or None
    db.commit()
    return UserResponse.model_validate(current_user)
