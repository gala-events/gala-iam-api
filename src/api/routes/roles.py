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
from models import Role, RoleCreate, RoleManager, RolePartial
from utils import get_db, json_merge_patch
from utils.exceptions import RecordNotFoundException

routes = APIRouter()


@routes.post("/roles", response_model=Role)
def create_role_api(role: RoleCreate, response: Response, db=Depends(get_db)):
    try:
        new_role = RoleManager.create(db, role)
        response.status_code = HTTP_201_CREATED
        return new_role
    except ValidationError:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to create role"))


@routes.get("/roles", response_model=List[Role])
def get_roles_api(response: Response,
                  db=Depends(get_db),
                  skip: int = 0,
                  limit: int = 25,
                  search: str = None,
                  sort: List[str] = Query([], alias="sort_by")):
    try:
        response.status_code = HTTP_200_OK
        roles = RoleManager.find(db, skip=skip, limit=limit,
                                 search=search, sort=sort)
        return roles
    except Exception as exc:
        response.status_code = HTTP_500_INTERNAL_SERVER_ERROR
        return JSONResponse(dict(error="Failed to get roles. %s" % str(exc)))


@routes.get("/roles/{role_id}", response_model=Role)
def get_role_api(role_id: str, response: Response, db=Depends(get_db)):
    try:
        role = RoleManager.find_by_uuid(db, role_id)
        return role
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))


@routes.put("/roles/{role_id}", response_model=Role)
def update_role_api(role_id: str, role: RoleCreate, response: Response, db=Depends(get_db)):
    try:
        updated_role = RoleManager.update(db, role_id, role)
        return updated_role
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except ValidationError as exc:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to update %s role. %s" % (role_id, str(exc))))


@routes.patch("/roles/{role_id}", response_model=Role)
def partial_update_role_api(role_id: str, role: RolePartial, response: Response, db=Depends(get_db)):
    try:
        updated_role = RoleManager.partial_update(db, role_id, role)
        response.status_code = HTTP_200_OK
        return updated_role
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except ValidationError as exc:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to update %s role. %s" % (role_id, str(exc))))


@routes.delete("/roles/{role_id}")
def delete_role_api(role_id: str, response: Response, db=Depends(get_db)):
    try:
        RoleManager.delete(db, role_id)
        response.status_code = HTTP_204_NO_CONTENT
        return JSONResponse(dict(message="Role %s deleted successfully." % role_id))
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
