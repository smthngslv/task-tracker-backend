from typing import Optional

from pydantic import Field, constr, EmailStr

from task_tracker_backend.dataclasses import BaseModel, UserData, TaskData


class APIAccessTokenPayload(BaseModel):
    user_id: str


class APIConfirmTokenPayload(BaseModel):
    email: EmailStr


class APIConfirmToken(BaseModel):
    confirm_token: str


class APIAccessToken(BaseModel):
    access_token: str


class APIHTTPError(BaseModel):
    """
    Represents exception.
    """

    detail: str = Field(..., title='Exception information.')


class User(UserData):
    id: str


class UserAuthentication(BaseModel):
    username: str
    password: str


class UserRegistration(BaseModel):
    email: EmailStr


class UserRegistrationConfirm(BaseModel):
    confirm_token: str
    username: constr(regex=r'^[a-zA-Z0-9]([._-](?![._-])|[a-zA-Z0-9]){3,18}[a-zA-Z0-9]$')
    password: constr(min_length=8, max_length=64, strip_whitespace=True)
    role: Optional[constr(max_length=64)]


class UserChangingPassword(BaseModel):
    old_password: str
    new_password: constr(min_length=8, max_length=64, strip_whitespace=True)


class UserResetPassword(BaseModel):
    email: EmailStr


class UserResetPasswordConfirm(BaseModel):
    confirm_token: str
    password: constr(min_length=8, max_length=64, strip_whitespace=True)


class Task(TaskData):
    id: str


class TaskList(BaseModel):
    tasks: list[Task]
