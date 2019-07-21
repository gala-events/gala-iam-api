from datetime import datetime
from enum import Enum
from typing import List, Union
from uuid import UUID

from pydantic import BaseModel

from models.base_record import BaseRecord

RESOURCE_MODEL_NAME = "resources"


class ResourceKind(str, Enum):
    EVENT = "EVENT"


class ResourceCreate(BaseModel):
    name: str
    kind: ResourceKind


class Resource(BaseRecord, ResourceCreate):
    @property
    def model_name(self):
        return RESOURCE_MODEL_NAME


class ResourcePartial(BaseModel):
    name: str = None
    kind: ResourceKind = None
