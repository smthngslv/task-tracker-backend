from bson import ObjectId
# noinspection PyProtectedMember
from motor.motor_asyncio import AsyncIOMotorCollection

from task_tracker_backend.dataclasses import UserData
from task_tracker_backend.task_factory import TaskFactory


class User:
    def __init__(
            self, users_collection: AsyncIOMotorCollection, tasks_collection: AsyncIOMotorCollection, _id: ObjectId
    ) -> None:
        self.__id = _id
        self.__users_collection = users_collection
        self.__tasks_collection = tasks_collection

    @property
    def id(self) -> ObjectId:
        return self.__id

    @property
    def task_factory(self) -> TaskFactory:
        return TaskFactory(self.__tasks_collection, self.__id)

    @property
    async def data(self) -> UserData:
        return UserData.parse_obj(await self.__users_collection.find_one({'_id': self.__id}, {'_id': 0, 'password': 0}))

    async def update_data(self, data: UserData) -> None:
        await self.__users_collection.update_one({'_id': self.__id}, {'$set': data.dict()})
