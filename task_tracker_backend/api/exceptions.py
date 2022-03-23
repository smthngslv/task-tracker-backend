from bson.errors import InvalidId
from fastapi import status
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError

from task_tracker_backend.api import app
from task_tracker_backend.exceptions import (
    BaseError, UserNotFoundError, TaskNotFoundError, InvalidPasswordError,
    UserAlreadyExists
)


@app.exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR)
async def http_exception_handler(*_) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={'detail': 'Internal server error.'}
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(_, exception: ValidationError) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={'detail': exception.errors()}
    )


@app.exception_handler(InvalidId)
async def validation_exception_handler(*_) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={'detail': 'Invalid id.'}
    )


@app.exception_handler(BaseError)
def file_storage_exception_handler(_, exception: BaseError) -> ORJSONResponse:
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    if isinstance(exception, UserNotFoundError | TaskNotFoundError):
        status_code = status.HTTP_404_NOT_FOUND

    elif isinstance(exception, InvalidPasswordError):
        status_code = status.HTTP_403_FORBIDDEN

    elif isinstance(exception, UserAlreadyExists):
        status_code = status.HTTP_400_BAD_REQUEST

    return ORJSONResponse(status_code=status_code, content={'detail': str(exception)})
