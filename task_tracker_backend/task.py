from bson import ObjectId
# noinspection PyProtectedMember
from motor.motor_asyncio import AsyncIOMotorCollection

from task_tracker_backend.dataclasses import TaskData


class Task:
    def __init__(self, collection: AsyncIOMotorCollection, _id: ObjectId) -> None:
        self.__collection = collection
        self.__id = _id

    @property
    def id(self) -> ObjectId:
        return self.__id

    @property
    async def data(self) -> TaskData:
        return TaskData.parse_obj(
            await self.__collection.find_one({'_id': self.__id}, {'_id': 0, 'user_id': 0})
        )

    async def update_data(self, data: TaskData) -> None:
        await self.__collection.update_one({'_id': self.__id}, {'$set': data.dict()})
