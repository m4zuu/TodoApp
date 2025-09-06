from fastapi import APIRouter, HTTPException, Depends, Path
from App.Database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from App.models import Todos, Users
from starlette import status
from pydantic import BaseModel, Field
from auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(
    prefix='/user',
    tags=['user']
)

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        # Yield means only the code prior to and including the yield statement is
        # executed before sending a res´ponse
        yield db
    finally:
        db.close()

# DB dependency Injection, value type Annotated, and 2 steps to complete before sending a response
db_dependency= Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency,
                   db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    return db.query(Users).filter(Users.id == user.get('id')).first()

@router.put('/password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency,
                          db: db_dependency,
                          user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401,
                            detail='Authentication Failed')
    
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail='Error on Password Change')
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()

@router.put("/phone_number/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependency,
                              db: db_dependency,
                              phone_number: str):
    if user is None:
        raise HTTPException(status_code=401,
                            detail='Authentication Failed')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    user_model.phone_number = phone_number

    db.add(user_model)
    db.commit()
