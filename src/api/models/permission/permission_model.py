from datetime import datetime
from enum import Enum
from typing import List, Union
from uuid import UUID

from pydantic import BaseModel

from models.base_record import BaseRecord, BaseRecordConfig

PERMISSION_MODEL_NAME = "permissions"


class PermissionSubjectKind(str, Enum):
    USER = "USER"
    SERVICE_ACCOUNT = "SERVICE_ACCOUNT"
    GROUP = "GROUP"


class PermissionSubject(BaseRecordConfig):
    kind: PermissionSubjectKind
    name: str


class PermissionMetadata(BaseRecordConfig):
    name: str


class PermissionCreate(BaseRecordConfig):
    metadata: PermissionMetadata
    role: str
    subjects: List[PermissionSubject] = None


class Permission(BaseRecord, PermissionCreate):
    metadata: PermissionMetadata
    @property
    def model_name(self):
        return PERMISSION_MODEL_NAME


class PermissionPartial(BaseRecordConfig):
    metadata: PermissionMetadata = None
    role: str = None
    subjects: List[PermissionSubject]
