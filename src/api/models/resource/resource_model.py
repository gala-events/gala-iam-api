from datetime import datetime
from enum import Enum
from typing import List, Union
from uuid import UUID

from pydantic import BaseModel

from models.base_record import BaseRecord, BaseRecordConfig

RESOURCE_MODEL_NAME = "resources"


class ResourceKind(str, Enum):
    EVENT = "EVENT"


class ResourceMetadata(BaseRecordConfig):
    name: str
    resource_kind: ResourceKind


class ResourceCreate(BaseRecordConfig):
    metadata: ResourceMetadata


class Resource(BaseRecord, ResourceCreate):
    metadata: ResourceMetadata
    @property
    def model_name(self):
        return RESOURCE_MODEL_NAME


class ResourcePartial(BaseRecordConfig):
    metadata: ResourceMetadata = None
