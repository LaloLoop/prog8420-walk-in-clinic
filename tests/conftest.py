import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine.mock import MockConnection
from sqlalchemy.orm import sessionmaker

from src.repos.entities import Base


@pytest.fixture
def engine() -> MockConnection:
    return create_engine('sqlite:///:memory:', echo=True)


@pytest.fixture
def session(engine):
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    return Session()
