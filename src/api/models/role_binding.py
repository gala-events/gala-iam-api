from datetime import datetime
from enum import Enum
from typing import List, Union
from uuid import UUID

from pydantic import BaseModel

from models.role import RoleType
from models.service_account import ServiceAccount
from models.user import User
from models.user_group import UserGroup


class RoleBindingType(str, Enum):
    SYSTEM_WIDE = "SystemWide"
    EVENT_WIDE = "EventWide"


class RoleBindingMetadata(BaseModel):
    name: str
    namespace: List[str]


class RoleBindingRoleRef(BaseModel):
    kind: RoleType
    name: str


class RoleBindingSubjectKind(str, Enum):
    USER = User.__name__
    SERVICE_ACCOUNT = ServiceAccount.__name__
    USER_GROUP = UserGroup.__name__


class RoleBindingSubject(BaseModel):
    kind: RoleBindingSubjectKind
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
