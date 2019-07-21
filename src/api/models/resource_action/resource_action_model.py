from datetime import datetime
from enum import Enum
from typing import List, Union
from uuid import UUID

from pydantic import BaseModel

from models.base_record import BaseRecord

RESOURCE_ACTION_MODEL_NAME = "resource_actions"


class ResourceActionCreate(BaseModel):
    name: str
    kind: str


class ResourceAction(BaseRecord, ResourceActionCreate):
    def model_name(self):
        return RESOURCE_ACTION_MODEL_NAME


class ResourceActionPartial(BaseModel):
    name: str = None
    kind: str = None
