import os
from datetime import datetime

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Integer,
    LargeBinary,
    String,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

if os.environ.get("ENV", "dev").lower() == "prod":
    DATABASE_URL = (
        f"postgresql+asyncpg://{os.environ.get('DB_USER', 'core')}:"
        f"{os.environ.get('DB_PASSWORD', 'core')}@{os.environ.get('DB_HOST', 'localhost')}:"
        f"{os.environ.get('DB_PORT', 5432)}/{os.environ.get('DB_NAME', 'core')}"
    )
else:
    DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.now, index=True)


class Cache(BaseModel):
    __tablename__ = "cache"
    key = Column(String(255), unique=True, index=True)
    data = Column(LargeBinary)
    access_at = Column(DateTime, index=True, nullable=True, onupdate=datetime.now)


class Keys(BaseModel):
    __tablename__ = "keys"
    key = Column(String(255), unique=True, index=True)
    data = Column(JSON)
    access_at = Column(DateTime, index=True, nullable=True, onupdate=datetime.now)


class Webhooks(BaseModel):
    __tablename__ = "webhooks"
    key = Column(String(255), unique=True, index=True)
    data = Column(JSON)
    sent_at = Column(DateTime, index=True, nullable=True)
