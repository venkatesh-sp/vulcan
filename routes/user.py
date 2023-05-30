from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from models import get_db, User, Account, SubAccount

from auth import (
    get_current_user,
    hash_password,
    authenticate_user,
    create_access_token,
    create_refresh_token,
)

router = APIRouter()


# User creation request model
class UserCreate(BaseModel):
    username: str
    password: str


# User login request model
class UserLogin(BaseModel):
    username: str
    password: str


# Signup API
@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )
    # Creates a new user with unique username
    new_user = User(username=user.username, password=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    #  Creates user account with unique account name
    user_account = Account(name=f"{new_user.username}_account", user_id=new_user.id)
    db.add(user_account)
    db.commit()
    db.refresh(user_account)

    #  Creates user's sub-account
    user_sub_account = SubAccount(
        name=f"{new_user.username}_sub_account", account_id=user_account.id
    )
    db.add(user_sub_account)
    db.commit()
    db.refresh(user_sub_account)
    return {"message": "User created successfully"}


# Login API
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    authenticated_user = authenticate_user(db, user.username, user.password)
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Credentials"
        )
    access_token = create_access_token(authenticated_user)
    refresh_token = create_refresh_token(authenticated_user)
    return {"access_token": access_token, "refresh_token": refresh_token}


# Protected route
@router.get("/me", summary="Get User")
def protected_route(user: User = Depends(get_current_user)):
    return {"message": f"Hello, {user.username}!"}
