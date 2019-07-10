from datetime import datetime
from enum import Enum
from typing import List, Union
from uuid import UUID

from pydantic import BaseModel

from models.role import RoleType


class RoleBindingType(str, Enum):
    SYSTEM_WIDE = "SystemWide"
    EVENT_WIDE = "EventWide"


class RoleBindingMetadata(BaseModel):
    name: str
    namespace: List[str]


class RoleBindingRoleRef(BaseModel):
    kind: RoleType
    name: str


class RoleBindingSubject(BaseModel):
    kind: Union[str]
    name: str


class RoleBindingCreate(BaseModel):
    kind: RoleBindingType
    metadata: RoleBindingMetadata
    role: RoleBindingRoleRef
    subjects: List[RoleBindingSubject]


class RoleBinding(RoleBindingCreate):
    uuid: UUID


class RoleBindingPartial(BaseModel):
    kind: RoleBindingType = None
    metadata: RoleBindingMetadata = None
    role: RoleBindingRoleRef = None
    subjects: List[RoleBindingSubject] = None
