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
from models import Permission, PermissionCreate, PermissionPartial
from utils import get_db, json_merge_patch
from utils.exceptions import RecordNotFoundException

routes = APIRouter()


def create_permission(permission: PermissionCreate, db: Database):
    permission_data = permission.dict()
    permission_id = CRUD.create(db, "permissions", permission_data)
    permission_record = CRUD.find_by_uuid(
        db, "permissions", str(permission_id))
    permission = Permission(**permission_record)
    return permission


def get_permissions(db,
                    skip: int = 0,
                    limit: int = 25,
                    search: str = None,
                    sort: List[str] = Query([], alias="sort_by")):
    filter_params = dict()
    search_fields = ["uuid", "name"]
    if search:
        map(lambda search_field: filter_params.update(
            search_field=re.compile(search)), search_fields)

    data = CRUD.find(db, "permissions", skip=skip,
                     limit=limit,
                     filter_params=filter_params,
                     sort=sort)
    return [Permission(**d) for d in data]


def get_permission(permission_id: str, db):
    data = CRUD.find_by_uuid(db, "permissions", permission_id)
    return Permission(**data)


def update_permission(permission_id: str, permission: PermissionCreate, db):
    data = CRUD.update(db, "permissions",
                       permission_id, permission.dict())
    return Permission(**data)


def partial_update_permission(permission_id: str, permission: PermissionPartial, db):
    existing_permission = CRUD.find_by_uuid(
        db, "permissions", permission_id)
    updated_permission = json_merge_patch(
        existing_permission, permission.dict(skip_defaults=True))
    data = CRUD.update(db, "permissions", permission_id,
                       updated_permission)
    return Permission(**data)


def delete_permission(permission_id: str, db):
    resp = CRUD.delete(db, "permissions", permission_id)
    return resp


@routes.post("/permissions", response_model=Permission)
def create_permission_api(permission: PermissionCreate, db=Depends(get_db)):
    permission = create_permission(permission, db)
    return permission


@routes.get("/permissions", response_model=List[Permission])
def get_permissions_api(db=Depends(get_db),
                        skip: int = 0,
                        limit: int = 25,
                        search: str = None,
                        sort: List[str] = Query([], alias="sort_by")):
    permissions = get_permissions(
        db=db, skip=skip, limit=limit, search=search, sort=sort)
    return permissions


@routes.get("/permissions/{permission_id}", response_model=Permission)
def get_permission_api(permission_id: str, db=Depends(get_db)):
    permission = get_permission(permission_id, db)
    return permission


@routes.put("/permissions/{permission_id}", response_model=Permission)
def update_permission_api(permission_id: str, permission: PermissionCreate, response: Response, db=Depends(get_db)):
    try:
        update_permission(permission_id, permission, db)
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to update %s record" % permission_id))


@routes.patch("/permissions/{permission_id}", response_model=Permission)
def partial_update_permission_api(permission_id: str, permission: PermissionPartial, db=Depends(get_db)):
    updated_permission = partial_update_permission(
        permission_id, permission, db)
    return updated_permission


@routes.delete("/permissions/{permission_id}")
def delete_permission_api(permission_id: str, response: Response, db=Depends(get_db)):
    try:
        delete_permission(permission_id, db)
        response.status_code = HTTP_204_NO_CONTENT
        return JSONResponse(dict(message="Permission %s deleted successfully." % permission_id))
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to delete Permission %s." % permission_id))
