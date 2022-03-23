class BaseError(Exception):
    pass


class UserNotFoundError(BaseError):
    pass


class TaskNotFoundError(BaseError):
    pass


class InvalidPasswordError(BaseError):
    pass


class UserAlreadyExists(BaseError):
    pass
