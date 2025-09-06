from Database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey # type: ignore

# Here we create the actual tables that are going to be created in our database
class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=False)
    role = Column(String)
    phone_number = Column(String)


class Todos(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True,index=True, autoincrement=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
