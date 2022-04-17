from datetime import datetime
from typing import AsyncGenerator

from bson import ObjectId
from fastapi import APIRouter, Depends, Body, status, Path, File, HTTPException
from ics import Calendar, Event
from starlette.responses import StreamingResponse

from task_tracker_backend import User, Task
from task_tracker_backend.api.schemas import (
    TaskList, Task as TaskScheme
)
from task_tracker_backend.api.utils.dependencies import get_current_user, get_current_task
from task_tracker_backend.dataclasses import TaskData, TaskStatus

# To be included.
router = APIRouter(tags=['tasks', ], prefix='/tasks')


@router.get('', status_code=status.HTTP_200_OK, response_model=TaskList)
async def get_all(user: User = Depends(get_current_user)) -> TaskList:
    tasks = []
    for task in await user.task_factory.list:
        tasks.append(TaskScheme(id=str(task.id), **(await task.data).dict()))

    return TaskList(tasks=tasks)


@router.get('/{task}', status_code=status.HTTP_200_OK, response_model=TaskScheme)
async def get(task: Task = Depends(get_current_task)) -> TaskScheme:
    return TaskScheme(id=str(task.id), **(await task.data).dict())


@router.get('/{task}/export', status_code=status.HTTP_200_OK, response_model=TaskScheme)
async def export(task: Task = Depends(get_current_task)) -> StreamingResponse:
    data = await task.data
    calendar = Calendar()
    calendar.events.add(
        Event(
            name=data.name,
            begin=datetime.now(),
            end=max(datetime.now(), data.deadline),
            description=data.description,
            categories=set(data.tags)
        )
    )

    async def iterator() -> AsyncGenerator[bytes, None]:
        yield str(calendar).encode()

    return StreamingResponse(
        iterator(),
        media_type='text/calendar',
        headers={'Content-Disposition': f'attachment; filename="task-{task.id}.ics"'}
    )


@router.post('/new', status_code=status.HTTP_201_CREATED, response_model=TaskScheme)
async def create(user: User = Depends(get_current_user), data: TaskData = Body(...)) -> TaskScheme:
    task = await user.task_factory.create(data)
    return TaskScheme(id=str(task.id), **data.dict())


@router.post('/import', status_code=status.HTTP_201_CREATED, response_model=TaskScheme)
async def import_(user: User = Depends(get_current_user), data: bytes = File(...)) -> TaskScheme:
    calendar = Calendar(data.decode())
    if len(calendar.events) != 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Calendar should contain only one event.')

    event = list(calendar.events)[0]
    data = TaskData(
        name=event.name,
        deadline=event.end.datetime,
        description=event.description,
        tags=list(event.categories),
        status=TaskStatus.BACKLOG
    )

    task = await user.task_factory.create(data)
    return TaskScheme(id=str(task.id), **data.dict())


@router.patch('/{task}', status_code=status.HTTP_204_NO_CONTENT)
async def update(data: TaskData = Body(...), task: Task = Depends(get_current_task)) -> None:
    await task.update_data(data)


@router.delete('/{task}', status_code=status.HTTP_202_ACCEPTED)
async def delete(user: User = Depends(get_current_user), task_id: str = Path(..., alias='task')) -> None:
    await user.task_factory.delete(ObjectId(task_id))
