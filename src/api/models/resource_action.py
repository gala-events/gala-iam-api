from datetime import datetime
from enum import Enum
from typing import List, Union
from uuid import UUID

from pydantic import BaseModel

from models.resource import ResourceKind


class ResourceActionCreate(BaseModel):
    name: str
    kind: ResourceKind


class ResourceAction(ResourceActionCreate):
    uuid: UUID


class ResourceActionPartial(BaseModel):
    name: str = None
    kind: ResourceKind = None
