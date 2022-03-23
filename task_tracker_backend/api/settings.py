from typing import Optional, Type

from pydantic import BaseSettings, Extra, validator, Field


class APISettings(BaseSettings):
    jwt_key: str = Field(..., title='Used for JWT authentication.')
    mongodb_url: str = Field(..., title='URL of MongoDB server.')
    root_path: Optional[str] = Field(None, title='API URL prefix.')

    smtp_host: str = Field(..., title='Used for SMTP authentication.')
    smtp_port: int = Field(..., title='Used for SMTP authentication.')
    smtp_username: str = Field(..., title='Used for SMTP authentication.')
    smtp_password: str = Field(..., title='Used for SMTP authentication.')

    @validator('jwt_key')
    def __validate_key(cls: Type['APISettings'], value: str) -> str:
        if len(value) < 32:
            raise ValueError('Key should be at least 32 bytes long.')

        return value

    class Config:
        extra = Extra.forbid
        case_sensitive = False

        env_file = '.env'
        env_prefix = 'TASK_TRACKER_BACKEND_API_'
