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
from models import Permission, PermissionCreate, PermissionManager, PermissionPartial
from utils import get_db, json_merge_patch
from utils.exceptions import RecordNotFoundException

routes = APIRouter()


@routes.post("/permissions", response_model=Permission)
def create_permission_api(permission: PermissionCreate, response: Response, db=Depends(get_db)):
    try:
        new_permission = PermissionManager.create(db, permission)
        response.status_code = HTTP_201_CREATED
        return new_permission
    except ValidationError as exc:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse({"error": "Failed to create permission: %s" % exc.raw_errors})


@routes.get("/permissions", response_model=List[Permission])
def get_permissions_api(response: Response,
                        db=Depends(get_db),
                        skip: int = 0,
                        limit: int = 25,
                        search: str = None,
                        sort: List[str] = Query([], alias="sort_by")):
    try:
        response.status_code = HTTP_200_OK
        permissions = PermissionManager.find(db, skip=skip, limit=limit,
                                             search=search, sort=sort)
        return permissions
    except Exception as exc:
        response.status_code = HTTP_500_INTERNAL_SERVER_ERROR
        return JSONResponse(dict(error="Failed to get permissions. %s" % str(exc)))


@routes.get("/permissions/{permission_id}", response_model=Permission)
def get_permission_api(permission_id: str, response: Response, db=Depends(get_db)):
    try:
        permission = PermissionManager.find_by_uuid(db, permission_id)
        return permission
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))


@routes.put("/permissions/{permission_id}", response_model=Permission)
def update_permission_api(permission_id: str, permission: PermissionCreate, response: Response, db=Depends(get_db)):
    try:
        updated_permission = PermissionManager.update(
            db, permission_id, permission)
        return updated_permission
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except ValidationError as exc:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to update %s permission. %s" % (permission_id, str(exc.raw_errors))))


@routes.patch("/permissions/{permission_id}", response_model=Permission)
def partial_update_permission_api(permission_id: str, permission: PermissionPartial, response: Response, db=Depends(get_db)):
    try:
        updated_permission = PermissionManager.partial_update(
            db, permission_id, permission)
        response.status_code = HTTP_200_OK
        return updated_permission
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except ValidationError as exc:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to update %s permission. %s" % (permission_id, str(exc.raw_errors))))


@routes.delete("/permissions/{permission_id}")
def delete_permission_api(permission_id: str, response: Response, db=Depends(get_db)):
    try:
        PermissionManager.delete(db, permission_id)
        response.status_code = HTTP_204_NO_CONTENT
        return JSONResponse(dict(message="Permission %s deleted successfully." % permission_id))
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
