from typing import AsyncGenerator
from fastapi import Depends
from fastapi_users import BaseUserManager
from fastapi_users_db_sqlalchemy import AsyncSession, SQLAlchemyUserDatabase
from models import Employee

from schemas import EmployeeCreate, EmployeeDB
from database import Base, async_session_maker, engine


SECRET = 'Wic-C0n3st0g4-4pp'

class UserManager(BaseUserManager[EmployeeCreate, EmployeeDB]):
    user_db_model = EmployeeDB
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET


# Dependency
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(EmployeeDB, session, Employee)

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)