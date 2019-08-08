from datetime import datetime
from enum import Enum
from typing import List, Union
from uuid import UUID

from pydantic import BaseModel
from pydantic.schema import Schema

from models.base_record import DEFAULT_NAMESPACE, BaseRecord, BaseRecordConfig

GROUP_MODEL_NAME = "groups"


class GroupSubjectKind(str, Enum):
    USER = "USER"
    SERVICE_ACCOUNT: "SERVICE_ACCOUNT"


class GroupSubject(BaseRecordConfig):
    kind: GroupSubjectKind
    name: str


class GroupMetadata(BaseRecordConfig):
    name: str


class GroupCreate(BaseRecordConfig):
    metadata: GroupMetadata
    subjects: List[GroupSubject]


class Group(BaseRecord, GroupCreate):
    metadata: GroupMetadata
    @property
    def model_name(self):
        return GROUP_MODEL_NAME


class GroupPartial(BaseRecordConfig):
    metadata: GroupMetadata = None
    subjects: List[GroupSubject] = []
