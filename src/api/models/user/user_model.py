from datetime import datetime
from typing import List, Union
from uuid import UUID

from pydantic import BaseModel

from models.base_record import BaseRecord
from models.base_record_manager import BaseRecordManager

USER_MODEL_NAME = "users"


class UserCreate(BaseModel):
    name: str


class User(BaseRecord, UserCreate):
    @property
    def model_name(self):
        return USER_MODEL_NAME


class UserPartial(BaseModel):
    name: str = None
