import hashlib
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, UserUpdate

router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"]
)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un utilisateur avec cet email existe déjà."
        )
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce nom d'utilisateur est déjà pris."
        )

    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password),
        full_name=user.full_name,
        bio=user.bio
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("", response_model=List[UserResponse])
def search_users(
    q: Optional[str] = Query(None, description="Filtrer par username, email ou nom complet"),
    db: Session = Depends(get_db)
):
    query = db.query(User)
    if q:
        search_pattern = f"%{q}%"
        query = query.filter(
            or_(
                User.username.ilike(search_pattern),
                User.email.ilike(search_pattern),
                User.full_name.ilike(search_pattern)
            )
        )
    return query.all()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable.")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable.")

    update_data = user_update.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"] != db_user.email:
        if db.query(User).filter(User.email == update_data["email"]).first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cet email est déjà utilisé.")

    if "username" in update_data and update_data["username"] != db_user.username:
        if db.query(User).filter(User.username == update_data["username"]).first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ce nom d'utilisateur est déjà pris.")

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable.")
    db.delete(db_user)
    db.commit()
    return None