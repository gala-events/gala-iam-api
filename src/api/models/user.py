from typing import List, Union
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    name: str


class User(UserCreate):
    uuid: UUID


class UserPartial(BaseModel):
    name: str = None
