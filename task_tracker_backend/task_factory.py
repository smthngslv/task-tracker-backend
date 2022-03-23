from bson import ObjectId
# noinspection PyProtectedMember
from motor.motor_asyncio import AsyncIOMotorCollection

from task_tracker_backend.dataclasses import TaskData
from task_tracker_backend.exceptions import TaskNotFoundError
from task_tracker_backend.task import Task


class TaskFactory:
    def __init__(self, collection: AsyncIOMotorCollection, user_id: ObjectId) -> None:
        self.__collection = collection
        self.__user_id = user_id

    @property
    async def list(self) -> list[Task]:
        tasks = []
        async for task in self.__collection.find({'user_id': self.__user_id}, {'_id': 1}):
            tasks.append(Task(self.__collection, task['_id']))

        return tasks

    async def get(self, _id: ObjectId) -> Task:
        if await self.__collection.count_documents({'_id': _id}) == 0:
            raise TaskNotFoundError(f'Task with id "{_id}" not found.')

        return Task(self.__collection, _id)

    async def create(self, data: TaskData) -> Task:
        result = await self.__collection.insert_one({**data.dict(), 'user_id': self.__user_id})
        return Task(self.__collection, result.inserted_id)

    async def delete(self, _id: ObjectId) -> None:
        result = await self.__collection.delete_one({'_id': _id})
        if result.deleted_count == 0:
            raise TaskNotFoundError(f'Task with id "{_id}" not found.')
