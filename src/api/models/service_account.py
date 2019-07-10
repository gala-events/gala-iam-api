from typing import List, Union
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ServiceAccountCreate(BaseModel):
    name: str = "system:service_account:scv_1"


class ServiceAccount(ServiceAccountCreate):
    uuid: UUID


class ServiceAccountPartial(BaseModel):
    name: str = None
