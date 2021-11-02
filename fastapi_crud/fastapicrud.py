from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from fastapi_crud.session import Session
from fastapi_crud.router import ModelRouter
from fastapi_crud.types import Model


class FastapiCRUD:
    def __init__(self, engine: AsyncEngine) -> None:
        self._session_maker = sessionmaker(engine, class_=Session)
        self.session: Session = Depends(self._session)

    async def _session(self) -> AsyncGenerator[Session, None]:
        async with self._session_maker() as session:
            yield session

    def create_router(self, model: Model) -> ModelRouter:
        return ModelRouter(model, self.session)
