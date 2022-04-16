from typing import AsyncGenerator
from fastapi import Depends
from fastapi_users import BaseUserManager
from fastapi_users_db_sqlalchemy import AsyncSession, SQLAlchemyUserDatabase

from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    JWTStrategy,
)

import models as m
from schemas import Employee, EmployeeCreate, EmployeeDB, EmployeeUpdate
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
    yield SQLAlchemyUserDatabase(EmployeeDB, session, m.Employee)

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


cookie_transport = CookieTransport(cookie_max_age=3600, cookie_httponly=False)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)
fastapi_users = FastAPIUsers(
    get_user_manager,
    [auth_backend],
    Employee,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeDB,
)

current_active_user = fastapi_users.current_user(active=True)