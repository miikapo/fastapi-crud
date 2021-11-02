from fastapi import APIRouter
from sqlalchemy import select, inspect as sqli
from sqlalchemy.orm import selectinload
from typing import Callable, Type
import inspect

import fastapi_crud.types as t
import fastapi_crud.schema as s
import fastapi_crud.config as c
from fastapi_crud.session import Session


def _modify_path_function_with_path_param(function, param):
    signature = inspect.signature(function)
    new_params = [
        inspect.Parameter(param, inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=str),
        signature.parameters["s"],
    ]
    if item_param := signature.parameters.get("item"):
        new_params.insert(0, item_param)
    new_signature = signature.replace(parameters=new_params)
    function.__signature__ = new_signature
    function.__annotations__ = function.__annotations__ | {param: str}


def getConfig(model: t.Model) -> c.CRUDConfig | None:
    for value in model.__dict__.values():
        try:
            if issubclass(value, c.CRUDConfig):
                return value
        except Exception:
            continue


class BaseRouter(APIRouter):
    def __init__(
        self,
        model: Type[t.Model],
        session_dependency: Session,
        config: Type[c.CRUDConfig],
        prefix: str = "",
        tags: list[str] = None,
    ) -> None:
        self.s = session_dependency
        self.model = model
        self.config = getConfig(model) or config
        super().__init__(prefix=prefix, tags=tags)


class ModelRouter(BaseRouter):
    def __init__(
        self,
        model: Type[t.Model],
        session_dependency: Session,
        config: Type[c.CRUDConfig] = c.CRUDConfig,
    ) -> None:
        super().__init__(
            model=model,
            session_dependency=session_dependency,
            config=config,
            prefix=f"/{model.__tablename__}",
            tags=[model.__name__],
        )
        self.out_schema = s.create_out_schema(model)
        self.create_schema = s.create_create_schema(
            model, exclude_fields=self.config.create_schema_exclude_fields
        )
        self.id = f"{model.__name__.lower()}_id"

        if self.config.read_one:
            self.add_api_route(
                methods=["GET"],
                path=f"/{{{self.id}}}",
                endpoint=self._get_one(),
                response_model=self.out_schema,
            )

        if self.config.read_all:
            self.add_api_route(
                methods=["GET"],
                path="",
                endpoint=self._get_all(),
                response_model=s.create_all_out_schema(model, self.out_schema),
            )

        if self.config.create:
            self.add_api_route(
                methods=["POST"], path="", endpoint=self._create(), response_model=self.out_schema
            )

        if self.config.delete:
            self.add_api_route(
                methods=["DELETE"],
                path=f"/{{{self.id}}}",
                endpoint=self._delete(),
                response_model=self.out_schema,
            )

        for r in sqli(model).relationships:
            self.include_router(
                RelationshipRouter(
                    r.mapper.class_,
                    parent=model,
                    relations=r.key,
                    session_dependency=session_dependency,
                    direction=r.direction.name,
                    config=c.RelationshipConfig,
                )
            )

    def _get_all(self) -> Callable:
        async def read_all(s: Session = self.s) -> dict[str, list[t.Model]]:
            stmt = select(self.model)
            result = await s.execute(stmt)
            return {"data": result.scalars().all()}

        return read_all

    def _get_one(self) -> Callable:
        async def read_one(s: Session = self.s, **kwargs) -> t.Model:
            return await s.get(self.model, kwargs.get(self.id))

        _modify_path_function_with_path_param(read_one, self.id)
        return read_one

    def _create(self) -> Callable:
        async def create(item: self.create_schema, s: Session = self.s) -> t.Model:  # type: ignore
            return await s.insert(self.model, item.dict())

        return create

    def _delete(self) -> Callable:
        async def delete(*args, s: Session = self.s, **kwargs) -> t.Model:
            to_delete = await s.get(self.model, kwargs.get(self.id))
            if to_delete:
                await s.delete(to_delete)
                await s.commit()
                return to_delete
            raise Exception("Missing")

        _modify_path_function_with_path_param(delete, self.id)
        return delete


class RelationshipRouter(BaseRouter):
    def __init__(
        self,
        model: Type[t.Model],
        parent: Type[t.Parent],
        relations: str,
        direction: str,
        session_dependency: Session,
        config: Type[c.CRUDConfig] = c.CRUDConfig,
    ) -> None:
        super().__init__(
            model=model,
            session_dependency=session_dependency,
            config=config,
        )
        self.parent = parent
        self.relation = relations
        self.is_to_one = direction.endswith("TOONE")
        self.out_schema = s.create_out_schema(model, parent)
        self.id = f"{parent.__name__.lower()}_id"
        self.create_schema = s.create_create_schema(
            model,
            exclude_fields=self.config.create_schema_exclude_fields + [self.id],
            parent=parent,
        )
        self.relation_name = self.model.__name__ if self.is_to_one else self.model.__tablename__

        if self.is_to_one:
            self.add_api_route(
                methods=["GET"],
                path=f"/{{{self.id}}}/{self.relation_name.lower()}",
                endpoint=self._get(),
                response_model=self.out_schema,
            )
        else:
            self.add_api_route(
                methods=["GET"],
                path=f"/{{{self.id}}}/{self.relation_name.lower()}",
                endpoint=self._get(),
                response_model=s.create_all_out_schema(model, self.out_schema, parent),
            )
        self.add_api_route(
            methods=["POST"],
            path=f"/{{{self.id}}}/{self.relation_name.lower()}",
            endpoint=self._create(),
            response_model=self.out_schema,
        )

    def _get(self) -> Callable:
        async def read(*args, s: Session = self.s, **kwargs) -> dict[str, list[t.Model]]:

            stmt = (
                select(self.parent)
                .where(self.parent.id == kwargs.get(self.id))
                .options(selectinload(getattr(self.parent, self.relation)))
            )
            res = await s.execute(stmt)
            parent = res.scalars().one()
            if self.is_to_one:
                return getattr(parent, self.relation, None)
            return {"data": getattr(parent, self.relation, [])}

        _modify_path_function_with_path_param(read, self.id)
        read.__name__ = f"Read {self.relation_name}"
        return read

    def _create(self) -> Callable:
        async def create(item: self.create_schema, s: Session = self.s, **kwargs) -> t.Model:  # type: ignore  # NOQA: E501
            parent = await s.get(self.parent, kwargs.get(self.id))
            item = item.dict()
            item[self.id] = parent.id
            return await s.insert(self.model, item)

        _modify_path_function_with_path_param(create, self.id)
        create.__name__ = f"Create {self.relation_name}"
        return create
