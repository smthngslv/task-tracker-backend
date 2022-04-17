from fastapi import APIRouter, Depends, Body, status, HTTPException

from task_tracker_backend import UserFactory, User
from task_tracker_backend.api import factory, jwt, email
from task_tracker_backend.api.schemas import (
    UserRegistration, APIAccessToken, APIAccessTokenPayload,
    User as UserSchema, APIConfirmTokenPayload, UserRegistrationConfirm, UserAuthentication, APIConfirmToken,
    UserChangingPassword, UserResetPassword, UserResetPasswordConfirm
)

from task_tracker_backend.api.utils.dependencies import get_current_user
from task_tracker_backend.dataclasses import UserData

# To be included.
router = APIRouter(tags=['users', ], prefix='/users')


@router.post('/authenticate', status_code=status.HTTP_200_OK, response_model=APIAccessToken)
async def authenticate(
        data: UserAuthentication = Body(...), user_factory: UserFactory = Depends(factory)
) -> APIAccessToken:
    user = await user_factory.authenticate(data.username, data.password)
    return APIAccessToken(access_token=jwt.encode(APIAccessTokenPayload(user_id=str(user.id))))


@router.get('/me', status_code=status.HTTP_200_OK, response_model=UserSchema)
async def get_me(user: User = Depends(get_current_user)) -> UserSchema:
    return UserSchema(id=str(user.id), **(await user.data).dict())


@router.post('/new', status_code=status.HTTP_202_ACCEPTED)
async def create(data: UserRegistration = Body(...)) -> None:
    encoded_token = jwt.encode(APIConfirmTokenPayload(email=data.email))
    await email.send(
        data.email,
        content=f"""<h1>Hello!</h1>
<p>You requested a registration on the Task Tracker website.</p>
<p>
  To proceed, please, follow this link:<br />
  <a href="https://tasktracker.gq/register/finish?token={encoded_token}">
    https://tasktracker.gq/register/finish?token={encoded_token}
  </a>
</p>
"""
    )


@router.post('/new/confirm', status_code=status.HTTP_201_CREATED, response_model=APIAccessToken)
async def confirm_creation(
        data: UserRegistrationConfirm = Body(...), user_factory: UserFactory = Depends(factory)
) -> APIAccessToken:
    try:
        token = jwt.decode(APIConfirmTokenPayload, data.confirm_token)

    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid or expired token.') from exc

    # Parse data.
    _data = UserData(email=token.email, username=data.username, role=data.role)

    user = await user_factory.create(_data, data.password)
    return APIAccessToken(access_token=jwt.encode(APIAccessTokenPayload(user_id=str(user.id))))


@router.patch('/me', status_code=status.HTTP_204_NO_CONTENT)
async def update(data: UserData = Body(...), user: User = Depends(get_current_user)) -> None:
    old_data = await user.data
    if old_data.email != data.email:
        encoded_token = jwt.encode(APIConfirmTokenPayload(email=data.email))
        await email.send(
            data.email,
            content=f"""<h1>Hello!</h1>
<p>You requested to change your email address on the Task Tracker website.</p>
<p>
  To proceed, please, follow this link (make sure you are logged in at first):<br />
  <a href="https://tasktracker.gq/settings/change_email?token={encoded_token}">
    https://tasktracker.gq/settings/change_email?token={encoded_token}
  </a>
</p>
"""
    )
        data.email = old_data.email

    await user.update_data(data)


@router.post('/me/confirm', status_code=status.HTTP_204_NO_CONTENT)
async def confirm_update(data: APIConfirmToken = Body(...), user: User = Depends(get_current_user)) -> None:
    try:
        token = jwt.decode(APIConfirmTokenPayload, data.confirm_token)

    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid or expired token.') from exc

    data = await user.data
    data.email = token.email
    await user.update_data(data)


@router.patch('/me/password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
        data: UserChangingPassword = Body(...),
        user: User = Depends(get_current_user),
        user_factory: UserFactory = Depends(factory)
) -> None:
    await user_factory.authenticate((await user.data).username, data.old_password)
    await user_factory.update_password(user.id, data.new_password)


@router.post('/password/reset', status_code=status.HTTP_202_ACCEPTED)
async def reset_password(data: UserResetPassword = Body(...), user_factory: UserFactory = Depends(factory)) -> None:
    await user_factory.get_by_email(data.email)
    encoded_token = jwt.encode(APIConfirmTokenPayload(email=data.email))
    await email.send(
        data.email,
        content=f"""<h1>Hello!</h1>
<p>You requested to change your password on the Task Tracker website.</p>
<p>
  To proceed, please, follow this link:<br />
  <a href="https://tasktracker.gq/login/restore?token={encoded_token}">
    https://tasktracker.gq/login/restore?token={encoded_token}
  </a>
</p>
"""
    )


@router.post('/password/reset/confirm', status_code=status.HTTP_200_OK)
async def reset_password(
        data: UserResetPasswordConfirm = Body(...),
        user_factory: UserFactory = Depends(factory)
) -> APIAccessToken:
    try:
        token = jwt.decode(APIConfirmTokenPayload, data.confirm_token)

    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid or expired token.') from exc

    user = await user_factory.get_by_email(token.email)
    await user_factory.update_password(user.id, data.password)

    return APIAccessToken(access_token=jwt.encode(APIAccessTokenPayload(user_id=str(user.id))))
