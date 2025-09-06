from sqlalchemy import create_engine
# ORM library, which is what our FastAPI application is going to use and be able
# to create a database and be anle to create a connection to a database and being able
# to use all of the database record within our application
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base



SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@localhost:5432/todosapp"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
