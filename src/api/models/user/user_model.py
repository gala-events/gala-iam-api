from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel

from models.base_record import BaseRecord, BaseRecordConfig
from models.base_record_manager import BaseRecordManager

USER_MODEL_NAME = "users"


class UserMetadata(BaseRecordConfig):
    name: str
    display_name: Optional[str] = None


class UserCreate(BaseRecordConfig):
    metadata: UserMetadata


class User(BaseRecord, UserCreate):
    metadata: UserMetadata
    @property
    def model_name(self):
        return USER_MODEL_NAME


class UserPartial(BaseRecordConfig):
    metadata: UserMetadata = None
