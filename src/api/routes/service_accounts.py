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


@routes.post("/service_accounts", response_model=ServiceAccount)
def create_service_account(service_account: ServiceAccountCreate, db=Depends(get_db)):
    service_account_id = CRUD.create(
        db, "service_accounts", service_account.dict())
    service_account_record = CRUD.find_by_uuid(
        db, "service_accounts", str(service_account_id))
    service_account = ServiceAccount(**service_account_record)
    return service_account


@routes.get("/service_accounts", response_model=List[ServiceAccount])
def get_service_accounts(db=Depends(get_db),
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


@routes.get("/service_accounts/{service_account_id}", response_model=ServiceAccount)
def get_service_account(service_account_id: str, db=Depends(get_db)):
    data = CRUD.find_by_uuid(db, "service_accounts", service_account_id)
    return ServiceAccount(**data)


@routes.put("/service_accounts/{service_account_id}", response_model=ServiceAccount)
def update_service_account(service_account_id: str, service_account: ServiceAccountCreate, response: Response, db=Depends(get_db)):
    try:
        data = CRUD.update(db, "service_accounts",
                           service_account_id, service_account.dict())
        return ServiceAccount(**data)
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to update %s record" % service_account_id))


@routes.patch("/service_accounts/{service_account_id}", response_model=ServiceAccount)
def partial_update_service_account(service_account_id: str, service_account: ServiceAccountPartial, db=Depends(get_db)):
    existing_service_account = CRUD.find_by_uuid(
        db, "service_accounts", service_account_id)
    updated_service_account = json_merge_patch(
        existing_service_account, service_account.dict(skip_defaults=True))
    data = CRUD.update(db, "service_accounts",
                       service_account_id, updated_service_account)
    return ServiceAccount(**data)


@routes.delete("/service_accounts/{service_account_id}")
def delete_service_account(service_account_id: str, response: Response, db=Depends(get_db)):
    try:
        CRUD.delete(db, "service_accounts", service_account_id)
        response.status_code = HTTP_204_NO_CONTENT
        return JSONResponse(dict(message="Event %s deleted successfully." % service_account_id))
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to delete Event %s." % service_account_id))
