import re
from os.path import join
from typing import Dict, List
from uuid import uuid4

from fastapi import APIRouter, Body, Depends, Query
from pydantic import BaseModel
from starlette.responses import JSONResponse, Response
from starlette.status import (HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
                              HTTP_404_NOT_FOUND)

from db import CRUD, Database
from models import ServiceAccount, ServiceAccountCreate, ServiceAccountPartial
from utils import get_db, json_merge_patch
from utils.exceptions import RecordNotFoundException

routes = APIRouter()


def create_service_account(service_account: ServiceAccountCreate, db: Database):
    service_account_data = service_account.dict()
    service_account_id = CRUD.create(
        db, "service_accounts", service_account_data)
    service_account_record = CRUD.find_by_uuid(
        db, "service_accounts", str(service_account_id))
    service_account = ServiceAccount(**service_account_record)
    return service_account


def get_service_accounts(db,
                         skip: int = 0,
                         limit: int = 25,
                         search: str = None,
                         sort: List[str] = Query([], alias="sort_by")):
    filter_params = dict()
    search_fields = ["uuid", "name"]
    if search:
        map(lambda search_field: filter_params.update(
            search_field=re.compile(search)), search_fields)

    data = CRUD.find(db, "service_accounts", skip=skip,
                     limit=limit,
                     filter_params=filter_params,
                     sort=sort)
    return [ServiceAccount(**d) for d in data]


def get_service_account(service_account_id: str, db):
    data = CRUD.find_by_uuid(db, "service_accounts", service_account_id)
    return ServiceAccount(**data)


def update_service_account(service_account_id: str, service_account: ServiceAccountCreate, db):
    data = CRUD.update(db, "service_accounts",
                       service_account_id, service_account.dict())
    return ServiceAccount(**data)


def partial_update_service_account(service_account_id: str, service_account: ServiceAccountPartial, db):
    existing_service_account = CRUD.find_by_uuid(
        db, "service_accounts", service_account_id)
    updated_service_account = json_merge_patch(
        existing_service_account, service_account.dict(skip_defaults=True))
    data = CRUD.update(db, "service_accounts", service_account_id,
                       updated_service_account)
    return ServiceAccount(**data)


def delete_service_account(service_account_id: str, db):
    resp = CRUD.delete(db, "service_accounts", service_account_id)
    return resp


@routes.post("/service_accounts", response_model=ServiceAccount)
def create_service_account_api(service_account: ServiceAccountCreate, db=Depends(get_db)):
    service_account = create_service_account(service_account, db)
    return service_account


@routes.get("/service_accounts", response_model=List[ServiceAccount])
def get_service_accounts_api(db=Depends(get_db),
                             skip: int = 0,
                             limit: int = 25,
                             search: str = None,
                             sort: List[str] = Query([], alias="sort_by")):
    service_accounts = get_service_accounts(
        db=db, skip=skip, limit=limit, search=search, sort=sort)
    return service_accounts


@routes.get("/service_accounts/{service_account_id}", response_model=ServiceAccount)
def get_service_account_api(service_account_id: str, db=Depends(get_db)):
    service_account = get_service_account(service_account_id, db)
    return service_account


@routes.put("/service_accounts/{service_account_id}", response_model=ServiceAccount)
def update_service_account_api(service_account_id: str, service_account: ServiceAccountCreate, response: Response, db=Depends(get_db)):
    try:
        update_service_account(service_account_id, service_account, db)
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to update %s record" % service_account_id))


@routes.patch("/service_accounts/{service_account_id}", response_model=ServiceAccount)
def partial_update_service_account_api(service_account_id: str, service_account: ServiceAccountPartial, db=Depends(get_db)):
    updated_service_account = partial_update_service_account(
        service_account_id, service_account, db)
    return updated_service_account


@routes.delete("/service_accounts/{service_account_id}")
def delete_service_account_api(service_account_id: str, response: Response, db=Depends(get_db)):
    try:
        delete_service_account(service_account_id, db)
        response.status_code = HTTP_204_NO_CONTENT
        return JSONResponse(dict(message="ServiceAccount %s deleted successfully." % service_account_id))
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to delete ServiceAccount %s." % service_account_id))
