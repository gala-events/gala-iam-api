from datetime import datetime
from enum import Enum
from typing import List, Union
from uuid import UUID

from pydantic import BaseModel


class ResourceKind(str, Enum):
    EVENT = "EVENT"


class ResourceCreate(BaseModel):
    name: str
    kind: ResourceKind


class Resource(ResourceCreate):
    uuid: UUID


class ResourcePartial(BaseModel):
    name: str = None
    kind: ResourceKind = None
