from datetime import datetime
from typing import Optional

import orjson
from pydantic import BaseModel as PydanticBaseModel, EmailStr, constr


def _orjson_dumps(*args, **kwargs) -> str:
    return orjson.dumps(*args, **kwargs).decode()


class BaseModel(PydanticBaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = _orjson_dumps


class UserData(BaseModel):
    email: EmailStr
    username: constr(regex=r'^[a-zA-Z0-9]([._-](?![._-])|[a-zA-Z0-9]){3,18}[a-zA-Z0-9]$')
    role: Optional[constr(max_length=64)]

    class Config:
        arbitrary_types_allowed = True


class TaskData(BaseModel):
    name: constr(max_length=64)
    tag: constr(regex=r'^[a-zA-Z0-9]([._-](?![._-])|[a-zA-Z0-9]){1,18}[a-zA-Z0-9]$')
    deadline: datetime
    description: Optional[constr(max_length=512)]

    class Config:
        arbitrary_types_allowed = True
