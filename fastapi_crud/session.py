from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Type

import fastapi_crud.types as t


class Session(AsyncSession):
    async def commit(self):
        try:
            await super().commit()
        except Exception as e:
            await self.rollback()
            raise e

    async def insert(self, model: Type[t.Model], item: t.Schema) -> t.Model | None:
        stmt = insert(model).values(item.dict())
        result = await self.execute(stmt)
        await self.commit()
        return await self.get(model, result)
