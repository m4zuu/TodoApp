from fastapi import APIRouter, HTTPException, Depends, Path, Request
from App.Database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from App.models import Todos
from starlette import status
from pydantic import BaseModel, Field
from auth import get_current_user
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix='/todos',
    tags=['todos']
)

templates = Jinja2Templates(directory="TodoApp/templates")

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

# Pydantic request for data validation
class TodoRequest(BaseModel):
    # We do not pass id, because it is autoincrement and unique, also indexed
    title : str = Field(min_length=3)
    description : str = Field(min_length=3, max_length=100)
    priority : int = Field(gt=0, lt=6)
    complete: bool

def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key='access_token')
    return redirect_response

from jose import JWTError
### Page ###
@router.get("/todo-page")
async def render_todo_page(request: Request,
                           db: db_dependency):
    try:
        user = get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
   
        todos = db.query(Todos).filter(Todos.owner_id == user.get('id')).all()
        return templates.TemplateResponse("todo.html", {'request': request, 'todos': todos, 'user': user})
        
    except:
        return redirect_to_login()
    

@router.get("/add-todo-page")
async def render_todo_page(request: Request):
    try:
        user = get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        
        return templates.TemplateResponse('add-todo.html', {'request': request, "user": user})
    except:
        return redirect_to_login()

@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request,
                                todo_id: int,
                                db: db_dependency):
    try:
        user = get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        
        todo = db.query(Todos).filter(Todos.id == todo_id).first()
        return templates.TemplateResponse('edit-todo.html', {'request': request,'todo':todo, 'user': user})
    except:
        return redirect_to_login()

### Endpoint ###

# Depends is Dependency Injection, this really just means in programming that we need
# to do something before we execute what we're trying to execute.
# This allow us to do some kind of code behind the scenes and then inject the dependencies,
# that this function relies on.
@router.get("/")
async def read_all(user: user_dependency, db: db_dependency, 
                   status_code=status.HTTP_200_OK):
    if user is None:
        raise HTTPException(status_code=401,
                            detail='Authentication Failed.')
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()
# This function relies on our DB opening up. be able to create a session and then return that
# information back to us and then closing the session behind the scenes

# We add more dynamic to out endpoint, calling status and adding a Path validation to todo_id
@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency,db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,
                            detail='Authentication Failed.')

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=401,
                            detail='Authentication Failed.')

    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get('id'))

    db.add(todo_model)
    db.commit()


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency,
                      db: db_dependency,
                      todo_request: TodoRequest, 
                      todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,
                            detail='Authentication Failed')

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency,
                      db: db_dependency,
                      todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,
                            detail='Authentication Failed')

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).delete()
    db.commit()