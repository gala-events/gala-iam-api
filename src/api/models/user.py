from typing import List, Union
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    name: str
    user_name: str
    email: str


class User(UserCreate):
    uuid: UUID


class UserPartial(BaseModel):
    name: str = None
    user_name: str = None
    email: str = None
