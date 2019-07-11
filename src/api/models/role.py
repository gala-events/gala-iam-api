from datetime import datetime
from enum import Enum
from typing import Dict, List, Union
from uuid import UUID

from pydantic import BaseModel


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
    name: str


class RoleRules(BaseModel):
    resources: List[str]
    resouceNames: List[str] = None
    access_type: List[RoleAccessType]


class RoleCreate(BaseModel):
    kind: RoleType
    metadata: RoleMeta
    rules: List[RoleRules]


class Role(RoleCreate):
    uuid: UUID


class RolePartial(BaseModel):
    kind: RoleType = None
    metadata: RoleMeta = None
    rules: List[RoleRules] = None
