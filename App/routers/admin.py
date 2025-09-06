from fastapi import APIRouter, HTTPException, Depends, Path
from App.Database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from App.models import Todos
from starlette import status
from pydantic import BaseModel, Field
from auth import get_current_user

router = APIRouter(
    prefix='/admin',
    tags=['admin']
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


@router.get('/todo', status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency,
                   db: db_dependency):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401,
                            detail='Authentication Failed')
    return db.query(Todos).all()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency,
                      db: db_dependency,
                      todo_id: int = Path(gt=0)):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401,
                            detail="Failed Authentication")
 
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()