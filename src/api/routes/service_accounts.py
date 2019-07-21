import re
from os.path import join
from typing import Dict, List
from uuid import uuid4

from fastapi import APIRouter, Body, Depends, Query
from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError
from starlette.responses import JSONResponse, Response
from starlette.status import (HTTP_200_OK, HTTP_201_CREATED,
                              HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
                              HTTP_404_NOT_FOUND,
                              HTTP_500_INTERNAL_SERVER_ERROR)

from db import CRUD, Database
from models import ServiceAccount, ServiceAccountCreate, ServiceAccountManager, ServiceAccountPartial
from utils import get_db, json_merge_patch
from utils.exceptions import RecordNotFoundException

routes = APIRouter()


@routes.post("/service_accounts", response_model=ServiceAccount)
def create_service_account_api(service_account: ServiceAccountCreate, response: Response, db=Depends(get_db)):
    try:
        new_service_account = ServiceAccountManager.create(db, service_account)
        response.status_code = HTTP_201_CREATED
        return new_service_account
    except ValidationError:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to create service_account"))


@routes.get("/service_accounts", response_model=List[ServiceAccount])
def get_service_accounts_api(response: Response,
                             db=Depends(get_db),
                             skip: int = 0,
                             limit: int = 25,
                             search: str = None,
                             sort: List[str] = Query([], alias="sort_by")):
    try:
        response.status_code = HTTP_200_OK
        service_accounts = ServiceAccountManager.find(db, skip=skip, limit=limit,
                                                      search=search, sort=sort)
        return service_accounts
    except Exception as exc:
        response.status_code = HTTP_500_INTERNAL_SERVER_ERROR
        return JSONResponse(dict(error="Failed to get service_accounts. %s" % str(exc)))


@routes.get("/service_accounts/{service_account_id}", response_model=ServiceAccount)
def get_service_account_api(service_account_id: str, response: Response, db=Depends(get_db)):
    try:
        service_account = ServiceAccountManager.find_by_uuid(
            db, service_account_id)
        return service_account
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))


@routes.put("/service_accounts/{service_account_id}", response_model=ServiceAccount)
def update_service_account_api(service_account_id: str, service_account: ServiceAccountCreate, response: Response, db=Depends(get_db)):
    try:
        updated_service_account = ServiceAccountManager.update(
            db, service_account_id, service_account)
        return updated_service_account
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except ValidationError as exc:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to update %s service_account. %s" % (service_account_id, str(exc))))


@routes.patch("/service_accounts/{service_account_id}", response_model=ServiceAccount)
def partial_update_service_account_api(service_account_id: str, service_account: ServiceAccountPartial, response: Response, db=Depends(get_db)):
    try:
        updated_service_account = ServiceAccountManager.partial_update(
            db, service_account_id, service_account)
        response.status_code = HTTP_200_OK
        return updated_service_account
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except ValidationError as exc:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to update %s service_account. %s" % (service_account_id, str(exc))))


@routes.delete("/service_accounts/{service_account_id}")
def delete_service_account_api(service_account_id: str, response: Response, db=Depends(get_db)):
    try:
        ServiceAccountManager.delete(db, service_account_id)
        response.status_code = HTTP_204_NO_CONTENT
        return JSONResponse(dict(message="ServiceAccount %s deleted successfully." % service_account_id))
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
