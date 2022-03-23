from fastapi import APIRouter

router = APIRouter()

from task_tracker_backend.api.views.users import router as users
from task_tracker_backend.api.views.tasks import router as tasks

router.include_router(users)
router.include_router(tasks)
