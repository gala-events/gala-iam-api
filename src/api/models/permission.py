from datetime import datetime
from enum import Enum
from typing import List, Union
from uuid import UUID

from pydantic import BaseModel

from models.role import RoleType
from models.service_account import ServiceAccount
from models.user import User
from models.user_group import UserGroup


class PermissionType(str, Enum):
    SYSTEM_WIDE = "SYSTEM_WIDE"
    EVENT_WIDE = "EVENT_WIDE"


class PermissionMetadata(BaseModel):
    name: str
    namespace: List[str]


class PermissionRoleRef(BaseModel):
    kind: RoleType
    name: str


class PermissionSubjectKind(str, Enum):
    USER = User.__name__
    SERVICE_ACCOUNT = ServiceAccount.__name__
    USER_GROUP = UserGroup.__name__


class PermissionSubject(BaseModel):
    kind: PermissionSubjectKind
    name: str


class PermissionCreate(BaseModel):
    kind: PermissionType
    metadata: PermissionMetadata
    role: PermissionRoleRef
    subjects: List[PermissionSubject]


class Permission(PermissionCreate):
    uuid: UUID


class PermissionPartial(BaseModel):
    kind: PermissionType = None
    metadata: PermissionMetadata = None
    role: PermissionRoleRef = None
    subjects: List[PermissionSubject] = None
