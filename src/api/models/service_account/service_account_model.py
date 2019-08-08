from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel

from models.base_record import BaseRecord, BaseRecordConfig
from models.base_record_manager import BaseRecordManager

SERVICE_ACCOUNT_MODEL_NAME = "service_accounts"


class ServiceAccountMetadata(BaseRecordConfig):
    name: str
    display_name: Optional[str] = None


class ServiceAccountCreate(BaseRecordConfig):
    metadata: ServiceAccountMetadata


class ServiceAccount(BaseRecord, ServiceAccountCreate):
    metadata: ServiceAccountMetadata
    @property
    def model_name(self):
        return SERVICE_ACCOUNT_MODEL_NAME


class ServiceAccountPartial(BaseRecordConfig):
    metadata: ServiceAccountMetadata = None
