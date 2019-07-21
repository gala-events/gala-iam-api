from datetime import datetime
from enum import Enum
from typing import List, Union
from uuid import UUID

from pydantic import BaseModel
from pydantic.schema import Schema

from models.base_record import BaseRecord, BaseRecordConfig

GROUP_MODEL_NAME = "groups"


class GroupSubjectKind(str, Enum):
    USER = "USER"
    SERVICE_ACCOUNT: "SERVICE_ACCOUNT"


class GroupSubject(BaseRecordConfig):
    name: str
    kind: GroupSubjectKind


class GroupCreate(BaseRecordConfig):
    name: str
    subjects: List[GroupSubject]


class Group(BaseRecord, GroupCreate):

    @property
    def model_name(self):
        return GROUP_MODEL_NAME


class GroupPartial(BaseRecordConfig):
    subjects: List[GroupSubject] = None
