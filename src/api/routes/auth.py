import base64
from datetime import timedelta
from typing import Optional, Union, List

from fastapi import APIRouter, Depends, Form, HTTPException, Header
from fastapi.security.oauth2 import OAuth2, OAuthFlowsModel
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from db import Database
from models import User, ServiceAccount
from models.auth.oauth2.outh2_grant_manager import (OAuth2GrantManager,
                                                    OAuth2GrantType, ACCESS_TOKEN_EXPIRE_MINUTES)
from models.auth.token import Token, TokenType
from utils import get_db

routes = APIRouter()

Subject = Union[User, ServiceAccount]


class OAuth2Bearer(OAuth2):
    def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


oauth_flows = OAuthFlowsModel(
    clientCredentials=dict(tokenUrl="/auth/oauth2/token"),
)

oauth2_scheme = OAuth2Bearer(flows=oauth_flows)


class OAuth2RequestForm:
    def __init__(self,
                 grant_type: OAuth2GrantType = Form(OAuth2GrantType.CLIENT_CREDENTIALS),
                 username: Optional[str] = Form(...),
                 password: Optional[str] = Form(...),
                 audience: str = Form(""),
                 scope: str = Form(""),
                 client_id: Optional[str] = Form(None, alias="clientId"),
                 client_secret: Optional[str] = Form(None, alias="clientSecret"),
                 authorization: Optional[str] = Header(None, alias="Authorization")
                 ):
        self.grant_type = grant_type
        self.username = username
        self.password = password
        self.scopes = scope.split()
        self.audiences = audience.split()
        self.client_id = client_id
        self.client_secret = client_secret

        if authorization:
            scheme, _, token = authorization.partition(" ")
            client_id_param, client_secret_param = base64.b64decode(token).decode("utf-8").split(":")
            self.client_id = client_id_param
            self.client_secret = client_secret_param


def create_access_token(db: Database, subject: Subject, scopes: List[str], audience: List[str]):
    if not scopes:
        scopes = []
    if not audience:
        audience = []

    token = OAuth2GrantManager.generate_token(db=db, subject=subject, audience=audience, scopes=scopes)
    return token


async def get_current_subject(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    subject = OAuth2GrantManager.get_subject(db, token)
    if subject is None:
        raise credentials_exception
    return subject


@routes.post("/auth/oauth2/token", response_model=Token)
async def generate_oauth2_token(form_data: OAuth2RequestForm = Depends(), db=Depends(get_db)):
    subject = OAuth2GrantManager.authenticate(db, strategy=form_data.grant_type, **form_data.__dict__)
    if not subject:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(db=db, subject=subject,
                                       scopes=form_data.scopes,
                                       audience=form_data.audiences)
    token_payload = {
        "access_token": access_token,
        "token_type": TokenType.BEARER,
        "expires_in": timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds()
    }
    return Token(**token_payload)


# @routes.get("/subject/me", response_model=Subject)
# async def read_users_me(current_subject: Subject = Depends(get_current_subject)):
#     return current_subject
