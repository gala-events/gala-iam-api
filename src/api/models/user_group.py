from datetime import datetime
from enum import Enum
from typing import List, Union
from uuid import UUID

from pydantic import BaseModel

from models.service_account import ServiceAccount
from models.user import User


class UserGroupSubjectKind(str, Enum):
    USER = User.__name__
    SERVICE_ACCOUNT: ServiceAccount.__name__


class UserGroupSubjects(BaseModel):
    name: str
    kind: UserGroupSubjectKind


class UserGroupCreate(BaseModel):
    name: str
    subjects: List[UserGroupSubjects]


class UserGroup(UserGroupCreate):
    uuid: UUID


class UserGroupPartial(BaseModel):
    subjects: List[UserGroupSubjects] = None
