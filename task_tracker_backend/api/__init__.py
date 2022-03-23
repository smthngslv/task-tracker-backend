from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware

from task_tracker_backend import UserFactory
from task_tracker_backend.api.settings import APISettings
from task_tracker_backend.api.utils import JWT, LazyObject
from task_tracker_backend.api.utils.email import Email

settings = APISettings()
app = FastAPI(
    title='TaskTrackerAPI',
    version='1.0.0',
    root_path=settings.root_path if settings.root_path is not None else '',
    default_response_class=ORJSONResponse
)

# Allow CORS.
app.add_middleware(
    CORSMiddleware, allow_credentials=True, allow_origins=['*'], allow_methods=['*'], allow_headers=['*']
)

# Initialize jwt.
jwt = JWT(settings.jwt_key)

# Create user factory.
factory = LazyObject(UserFactory, settings.mongodb_url)

# Email sender.
email = Email(settings.smtp_host, settings.smtp_port, settings.smtp_username, settings.smtp_password)


# Include exception handlers.
import task_tracker_backend.api.exceptions


# Include views.
from task_tracker_backend.api.views import router

app.include_router(router)
