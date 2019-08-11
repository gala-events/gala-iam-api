import os
from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from pydantic.main import BaseModel
from pydantic.schema import Schema

from models.service_account.service_account_model import ServiceAccount
from models.user.user_model import User

ISS = os.environ.get("IAM__ISS", "iam.gala.com")


class TokenData(BaseModel):
    iss: str = ISS
    sub: str
    aud: List[str]
    iat: datetime
    exp: datetime
    nbf: Optional[datetime] = None
    jti: Optional[str] = None
    sub_data: Union[User, ServiceAccount] = None
    scopes: List[str] = []


class TokenType(str, Enum):
    BEARER = "bearer"


class Token(BaseModel):
    access_token: str
    token_type: TokenType
    expires_in: int
    refresh_token: Optional[str]
    state: Optional[str]
