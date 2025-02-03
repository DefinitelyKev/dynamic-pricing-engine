from pydantic import BaseModel, ConfigDict
from datetime import datetime


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(from_attributes=True)


class BaseModelSchema(BaseSchema):
    """Base schema for database models."""

    created_at: datetime
    updated_at: datetime
