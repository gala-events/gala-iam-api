from datetime import datetime
from enum import Enum
from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel

from models.base_record import BaseRecord, BaseRecordConfig
from models.resource.resource_model import ResourceKind

RESOURCE_ACTION_MODEL_NAME = "resource_actions"


class ResourceActionMetadata(BaseRecordConfig):
    name: str
    resource_kind: ResourceKind
    resource: Optional[str] = None


class ResourceActionCreate(BaseRecordConfig):
    metadata: ResourceActionMetadata


class ResourceAction(BaseRecord, ResourceActionCreate):
    @property
    def model_name(self):
        return RESOURCE_ACTION_MODEL_NAME


class ResourceActionPartial(BaseRecordConfig):
    metadata: ResourceActionMetadata = None
