from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel

from models.base_record import BaseRecord, BaseRecordConfig
from models.resource.resource_model import ResourceKind

ROLE_MODEL_NAME = "roles"


class RoleMetadata(BaseRecordConfig):
    name: str


class RoleRule(BaseRecordConfig):
    resource: Optional[str] = None
    resource_kind: ResourceKind = ResourceKind.EVENT
    resource_actions: List[str]


class RoleCreate(BaseRecordConfig):
    metadata: RoleMetadata
    rules: List[RoleRule] = []


class Role(BaseRecord, RoleCreate):
    @property
    def model_name(self):
        return ROLE_MODEL_NAME


class RolePartial(BaseRecordConfig):
    metadata: RoleMetadata = None
    rules: List[RoleRule] = None
