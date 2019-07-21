from datetime import datetime
from enum import Enum
from typing import List, Union
from uuid import UUID

from pydantic import BaseModel

from models.base_record import BaseRecord

PERMISSION_MODEL_NAME = "permissions"


class PermissionType(str, Enum):
    SYSTEM_WIDE = "SYSTEM_WIDE"
    EVENT_WIDE = "EVENT_WIDE"


class PermissionMetadata(BaseModel):
    namespace: List[str]


class PermissionRoleRef(BaseModel):
    kind: str
    name: str


class PermissionSubjectKind(str, Enum):
    pass
    # USER = User.__name__
    # SERVICE_ACCOUNT = ServiceAccount.__name__
    # USER_GROUP = UserGroup.__name__


class PermissionSubject(BaseModel):
    kind: PermissionSubjectKind
    name: str


class PermissionCreate(BaseModel):
    kind: PermissionType
    name: str
    metadata: PermissionMetadata
    role: PermissionRoleRef
    subjects: List[PermissionSubject]


class Permission(BaseRecord, PermissionCreate):
    @property
    def model_name(self):
        return PERMISSION_MODEL_NAME


class PermissionPartial(BaseModel):
    kind: PermissionType = None
    name: str = None
    metadata: PermissionMetadata = None
    role: PermissionRoleRef = None
    subjects: List[PermissionSubject] = None
