from asyncio import run_coroutine_threadsafe, get_running_loop

from bson import ObjectId
# noinspection PyProtectedMember
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

from task_tracker_backend.dataclasses import UserData
from task_tracker_backend.exceptions import UserNotFoundError, InvalidPasswordError, UserAlreadyExists
from task_tracker_backend.user import User


class UserFactory:
    def __init__(
            self,
            mongodb_url: str,
            *,
            database: str = 'task-tracker',
            users_collection: str = 'users',
            tasks_collection: str = 'tasks'
    ) -> None:
        client = AsyncIOMotorClient(mongodb_url)
        self.__users_collection = client[database][users_collection]
        self.__tasks_collection = client[database][tasks_collection]
        self.__crypto_context = CryptContext(schemes=['bcrypt'])

        # Initialize indexes.
        run_coroutine_threadsafe(self.__initialize(), get_running_loop())

    async def get(self, _id: ObjectId) -> User:
        if await self.__users_collection.count_documents({'_id': _id}) == 0:
            raise UserNotFoundError(f'User with id "{_id}" not found.')

        return User(self.__users_collection, self.__tasks_collection, _id)

    async def get_by_email(self, email: str) -> User:
        user = await self.__users_collection.find_one({'email': email}, {'_id': 1})
        if user is None:
            raise UserNotFoundError(f'User with email "{email}" not found.')

        return User(self.__users_collection, self.__tasks_collection, user['_id'])

    async def authenticate(self, username: str, password: str) -> User:
        user = await self.__users_collection.find_one({'username': username}, {'_id': 1, 'password': 1})
        if user is None:
            raise UserNotFoundError(f'User with username "{username}" not found.')

        if self.__crypto_context.verify(password, user['password']):
            return User(self.__users_collection, self.__tasks_collection, user['_id'])

        raise InvalidPasswordError('Invalid password.')

    async def update_password(self, _id: ObjectId, password: str) -> None:
        result = await self.__users_collection.update_one(
            {'_id': _id}, {'$set': {'password': self.__crypto_context.hash(password)}}
        )

        if result.matched_count == 0:
            raise UserNotFoundError(f'User with id "{_id}" not found.')

    async def create(self, data: UserData, password: str) -> User:
        if await self.__users_collection.count_documents({'username': data.username}) != 0:
            raise UserAlreadyExists(f'User with username "{data.username}" already exists.')

        if await self.__users_collection.count_documents({'email': data.email}) != 0:
            raise UserAlreadyExists(f'User with email "{data.email}" already exists.')

        result = await self.__users_collection.insert_one(
            {**data.dict(), 'password': self.__crypto_context.hash(password)}
        )

        return User(self.__users_collection, self.__tasks_collection, result.inserted_id)

    async def __initialize(self) -> None:
        await self.__users_collection.create_index('email', unique=True)
        await self.__users_collection.create_index('username', unique=True)
