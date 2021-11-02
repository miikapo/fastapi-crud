from pydantic import BaseModel
from typing import TypeVar, Any

Model = TypeVar("Model", bound=Any)
Parent = TypeVar("Parent", bound=Any)
Schema = TypeVar("Schema", bound=BaseModel)
