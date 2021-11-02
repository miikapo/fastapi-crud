from pydantic import BaseModel as Schema, BaseConfig, create_model
from typing import Type, Optional, Any

import fastapi_crud.types as t
from fastapi_crud.type_map import DEFAULT_TYPE_MAP


def _create_field_definition(column) -> tuple:
    type = DEFAULT_TYPE_MAP.get(str(column.type), str)
    type = Optional[type] if column.nullable else type  # type: ignore
    default = None if column.nullable else ...
    return (type, default)


def _create_model(
    name: str, field_definitions: dict[str, tuple[Any, ...]], config: Type[BaseConfig] = None
) -> Type[Schema]:
    return create_model(
        name,
        __config__=config,
        __base__=None,
        __module__=__name__,
        __validators__=None,
        **field_definitions,
    )


class _OutSchemaConfig(BaseConfig):
    orm_mode = True


def create_out_schema(model: t.Model, parent: t.Parent = None) -> Type[Schema]:
    field_definitions = {col.name: _create_field_definition(col) for col in model.__table__.columns}
    name = f"{parent.__name__}{model.__name__}AllOut" if parent else f"{model.__name__}AllOut"
    return _create_model(name, field_definitions, _OutSchemaConfig)


def create_all_out_schema(model, out_schema: Type[Schema], parent: t.Parent = None):
    field_definitions = {"data": tuple([list[out_schema], ...])}  # type: ignore
    name = f"{parent.__name__}{model.__name__}Out" if parent else f"{model.__name__}Out"
    return _create_model(name, field_definitions, _OutSchemaConfig)


def create_create_schema(
    model: t.Model, exclude_fields: list[str], parent: t.Parent = None
) -> Type[Schema]:
    field_definitions = {
        col.name: _create_field_definition(col)
        for col in model.__table__.columns
        if col.name not in exclude_fields
    }
    name = f"{parent.__name__}{model.__name__}In" if parent else f"{model.__name__}In"
    return _create_model(name, field_definitions)
