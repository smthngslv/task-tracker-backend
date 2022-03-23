from bson import ObjectId
from fastapi import APIRouter, Depends, Body, status, Path

from task_tracker_backend import User, Task
from task_tracker_backend.api.schemas import (
    TaskList, Task as TaskScheme
)
from task_tracker_backend.api.utils.dependencies import get_current_user, get_current_task
from task_tracker_backend.dataclasses import TaskData

# To be included.
router = APIRouter(tags=['tasks', ], prefix='/tasks')


@router.get('', status_code=status.HTTP_200_OK, response_model=TaskList)
async def get(user: User = Depends(get_current_user)) -> TaskList:
    tasks = []
    for task in await user.task_factory.list:
        tasks.append(TaskScheme(id=str(task.id), **(await task.data).dict()))

    return TaskList(tasks=tasks)


@router.post('/new', status_code=status.HTTP_201_CREATED, response_model=TaskScheme)
async def create(user: User = Depends(get_current_user), data: TaskData = Body(...)) -> TaskScheme:
    task = await user.task_factory.create(data)
    return TaskScheme(id=str(task.id), **data.dict())


@router.patch('/{task}', status_code=status.HTTP_204_NO_CONTENT)
async def update(data: TaskData = Body(...), task: Task = Depends(get_current_task)) -> None:
    await task.update_data(data)


@router.delete('/{task}', status_code=status.HTTP_202_ACCEPTED)
async def delete(user: User = Depends(get_current_user), task_id: str = Path(..., alias='task')) -> None:
    await user.task_factory.delete(ObjectId(task_id))
