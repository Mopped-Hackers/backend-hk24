from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from application.main.config import settings

SQLALCHEMY_DATABASE_URL = settings.SQL_STRING

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

Base = declarative_base()
Base.query = SessionLocal.query_property()

from sqlalchemy import MetaData

metadata = MetaData()
