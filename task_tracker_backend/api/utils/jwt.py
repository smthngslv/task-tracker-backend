from typing import TypeVar, Type

from fastapi.encoders import jsonable_encoder
from jwt import PyJWT

from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class JWT:
    """
    Allows encoding and decoding JWT tokens.
    """

    Algorithm = 'HS256'

    def __init__(self, key: str) -> None:
        """
        Allows encoding and decoding JWT tokens.

        :param key: Key that used in operations.
        """
        self.__jwt = PyJWT()
        self.__key = key

    def decode(self, model: Type[T], token: str) -> T:
        """
        Decodes JWT token, validate it.

        :param model: Model of the token.
        :param token: String with JWT token.
        :return: Payload.
        """
        return model.parse_obj(self.__jwt.decode(token, self.__key, [self.Algorithm]))

    def encode(self, token: BaseModel) -> str:
        """
        Encodes a payload into JWT token.

        :param token: Payload.
        :return: String with JWT token.
        """
        return self.__jwt.encode(jsonable_encoder(token), self.__key, self.Algorithm)
