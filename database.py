import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


db_url = os.getenv("DATABASE_URL")

PG_URL_PREFIX = 'postgres://'
PG_ASYNC_URL_PREFIX = 'postgresql+asyncpg://'

if db_url is not None and PG_URL_PREFIX in db_url:
    db_url = db_url.replace(PG_URL_PREFIX, PG_ASYNC_URL_PREFIX)
else:
    "sqlite+aiosqlite:///./wic.sqlite"

SQLALCHEMY_DATABASE_URL = db_url


engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()