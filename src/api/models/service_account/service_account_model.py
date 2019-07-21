from datetime import datetime
from typing import List, Union
from uuid import UUID

from pydantic import BaseModel

from models.base_record import BaseRecord

SERVICE_ACCOUNT_MODEL_NAME = "service_accounts"


class ServiceAccountCreate(BaseModel):
    name: str = "system:service_account:scv_1"


class ServiceAccount(BaseRecord, ServiceAccountCreate):
    def model_name(self):
        return SERVICE_ACCOUNT_MODEL_NAME


class ServiceAccountPartial(BaseModel):
    name: str = None
