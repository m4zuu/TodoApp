from sqlalchemy import create_engine
# ORM library, which is what our FastAPI application is going to use and be able
# to create a database and be anle to create a connection to a database and being able
# to use all of the database record within our application
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base



SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@localhost:5432/todosapp"
# This is the url of our local database connection
# SQLALCHEMY_DATABASE_URL = 'postgresql:///./todos.sb' 

engine = create_engine(SQLALCHEMY_DATABASE_URL)
# Engine is something that we can use to be able to open up a connection and be able
# to user our database

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Each instance of the Session Local will have a database session
# The class itself is not a database session yet, we will add that later on, this is an
# instance of session local that will be able to become an actual database in the future

Base = declarative_base()
# The last thing we need to do is make sure that we can create a database object that we
# can then interact with later on
# What we're doing here is later on, we want to be able to call our Database.py file
# to be able to create a base which is an object of the database which is going to be able
# to then control our database
