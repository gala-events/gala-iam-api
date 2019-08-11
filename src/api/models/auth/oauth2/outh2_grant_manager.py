from datetime import timedelta, datetime
from enum import Enum
from typing import Union, List

import jwt
from jwt import PyJWTError

from db import Database
from utils.exceptions import RecordNotFoundException
from models import User, ServiceAccount, ServiceAccountManager, UserManager
from models.auth.oauth2.grants.client_credential import \
    ClientCredentialGrantManager
from models.auth.token import TokenData

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class OAuth2GrantType(str, Enum):
    CLIENT_CREDENTIALS = "client_credentials"


class OAuth2GrantManager:
    """OAuth2GrantManager to handle authentication, authrorization with various Grant flows
    """

    _grant_strategy = {
        OAuth2GrantType.CLIENT_CREDENTIALS: ClientCredentialGrantManager
    }

    @classmethod
    def authenticate(cls, db, strategy, *args, **kwargs):
        """Autheticates the principal based on strategy

        Arguments:
            db {Database} -- a live DatabaseConnection
        """
        print(f"strategy: {strategy}")
        if strategy in cls._grant_strategy:
            return cls._grant_strategy[strategy].authenticate(db, *args, **kwargs)
        raise Exception(f"Invalid Strategy [{strategy}].")

    @classmethod
    def generate_token(cls, db: Database, subject: Union[User, ServiceAccount],
                       audience: List[str],
                       scopes: List[str],
                       expires_delta: [int] = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
        expire_at = datetime.utcnow()
        if expires_delta:
            expire_at += timedelta(minutes=expires_delta)

        payload = {
            "sub": subject.uuid,
            "sub_data": subject,
            "iat": datetime.utcnow(),
            "nbf": datetime.utcnow(),
            "aud": audience,
            "exp": expire_at,
            "scopes": scopes
        }

        token_data = TokenData(**payload)
        to_encode = token_data.dict()
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @classmethod
    def get_subject(cls, db, token: str):
        try:
            manager = None
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], verify=False)
            sub_id: str = payload.get("sub")
            sub_kind: str = payload.get("sub_data", {}).get("kind")

            if not sub_id:
                return None

            if sub_kind == ServiceAccountManager.model_name:
                manager = ServiceAccountManager
            if sub_kind == UserManager.model_name:
                manager = UserManager

            if manager:
                subject = manager.find_by_uuid(db, sub_id)
                return subject

            return None

        except RecordNotFoundException:
            return None

        except PyJWTError:
            return None
