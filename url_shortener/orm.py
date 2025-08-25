from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlmodel import Field, Session, SQLModel, create_engine, select


class Base(AsyncAttrs, DeclarativeBase):
    pass


class URL(SQLModel, table=True):

    id: int | None = Field(default=None, primary_key=True)
    short_url: str | None = Field(default=None)
    original_url: str = Field(default=None)
