from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from ..Database import Base
from ..main import app
from ..routers.todos import get_db, get_current_user
from fastapi.testclient import TestClient
from fastapi import status
import pytest
from ..models import Todos, Users


SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@localhost:5432/testdb"

# check_same_thread is for sqlite databases specifically
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
   # connect_args={"check_same_thread": False},
    poolclass = StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def overrided_get_current_user():
    return {'username': 'codingwithRoby',
            'id': 1,
            'user_role': 'admin'}

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = overrided_get_current_user

client = TestClient(app)

@pytest.fixture
def test_todo():
    db = TestingSessionLocal()

    user = Users(
        id=1,  # Fuerzas el ID a 1 para que coincida con tu override
        username="codingwithRoby",
        hashed_password="fakepassword",  # Lo que uses normalmente
        role="admin"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
     
    todo = Todos(
        title = "Learn To Code",
        description = "Need to learn everyday",
        priority= 5,
        complete= False,
        owner_id= user.id
    )

    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.execute(text("DELETE FROM users;"))
        connection.commit()


def test_read_all_authenticated(test_todo):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1

    todo = data[0]
    assert todo['title'] == "Learn To Code"
    assert todo['description'] == "Need to learn everyday"
    assert todo['priority'] == 5
    assert todo['complete'] is False
    assert todo['owner_id'] == 1
    assert isinstance(todo['id'], int)  # Solo verificamos que sea int

