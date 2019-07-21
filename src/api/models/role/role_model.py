from datetime import datetime
from enum import Enum
from typing import Dict, List, Union
from uuid import UUID

from pydantic import BaseModel

from models.base_record import BaseRecord

ROLE_MODEL_NAME = "roles"


class RoleType(str, Enum):
    SYSTEM_WIDE = "SYSTEM_WIDE"
    EVENT_WIDE = "EVENT_WIDE"


class RoleAccessType(str, Enum):
    GET = "get"
    LIST = "list"
    UPDATE = "update"
    CREATE = "create"
    PATCH = "patch"
    DELETE = "delete"


class RoleMeta(BaseModel):
    namespace: List[str]


class RoleRules(BaseModel):
    resources: List[str]
    resouceNames: List[str] = None
    access_type: List[RoleAccessType]


class RoleCreate(BaseModel):
    name: str
    kind: RoleType
    metadata: RoleMeta
    rules: List[RoleRules]


class Role(BaseRecord, RoleCreate):
    @property
    def model_name(self):
        return ROLE_MODEL_NAME


class RolePartial(BaseModel):
    kind: RoleType = None
    name: str = None
    metadata: RoleMeta = None
    rules: List[RoleRules] = None
