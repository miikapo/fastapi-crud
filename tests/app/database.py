from typing import Type, TypeVar
from pydantic import BaseModel
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from tests.app.config import app_config
from tests.app.models import Base

SchemaObject = TypeVar("SchemaObject", bound=BaseModel)
ModelObject = TypeVar("ModelObject", bound=Base)


class _Session(AsyncSession):
    async def commit(self):
        try:
            await super().commit()
        except Exception as e:
            await self.rollback()
            raise e

    async def insert(self, model: Type[ModelObject], item: dict) -> ModelObject:
        stmt = insert(model).values(item)
        result = await self.execute(stmt)
        await self.commit()
        return await self.get(model, result.inserted_primary_key)


class Database:
    _engine = create_async_engine(app_config.SQLALCHEMY_DATABASE_URI, echo=True)
    _session_maker = sessionmaker(_engine, class_=_Session)

    @classmethod
    async def session(cls) -> _Session:
        async with cls._session_maker() as session:
            yield session


db = Database
