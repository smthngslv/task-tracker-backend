from bson import ObjectId
from fastapi import Security, HTTPException, status, Depends, Path
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from task_tracker_backend import User, UserFactory, Task
from task_tracker_backend.api import jwt, factory
from task_tracker_backend.api.schemas import APIAccessTokenPayload


async def get_access_token(credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())) -> APIAccessTokenPayload:
    try:
        return jwt.decode(APIAccessTokenPayload, credentials.credentials)

    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid or expired token.') from exc


async def get_current_user(
        user_factory: UserFactory = Depends(factory), token: APIAccessTokenPayload = Depends(get_access_token)
) -> User:
    return await user_factory.get(ObjectId(token.user_id))


async def get_current_task(user: User = Depends(get_current_user), task_id: str = Path(..., alias='task')) -> Task:
    return await user.task_factory.get(ObjectId(task_id))
