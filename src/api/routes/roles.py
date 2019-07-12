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
from models import Role, RoleCreate, RolePartial
from utils import get_db, json_merge_patch
from utils.exceptions import RecordNotFoundException

routes = APIRouter()


def create_role(role: RoleCreate, db: Database):
    role_data = role.dict()
    role_id = CRUD.create(db, "roles", role_data)
    role_record = CRUD.find_by_uuid(
        db, "roles", str(role_id))
    role = Role(**role_record)
    return role


def get_roles(db,
              skip: int = 0,
              limit: int = 25,
              search: str = None,
              sort: List[str] = None):
    filter_params = dict()
    search_fields = ["uuid", "name"]
    if search:
        map(lambda search_field: filter_params.update(
            search_field=re.compile(search)), search_fields)

    data = CRUD.find(db, "roles", skip=skip,
                     limit=limit,
                     filter_params=filter_params,
                     sort=sort)
    return [Role(**d) for d in data]


def get_role(role_id: str, db):
    data = CRUD.find_by_uuid(db, "roles", role_id)
    return Role(**data)


def get_role_by_name(name: str, db):
    data = get_roles(db, search=name)
    if len(data) == 0:
        raise ValueError("Role not found with name [%s]", name)
    if len(data) > 1:
        raise ValueError("Multiple Roles found with name [%s]", name)
    return data[0]


def update_role(role_id: str, role: RoleCreate, db):
    data = CRUD.update(db, "roles",
                       role_id, role.dict())
    return Role(**data)


def partial_update_role(role_id: str, role: RolePartial, db):
    existing_role = CRUD.find_by_uuid(
        db, "roles", role_id)
    updated_role = json_merge_patch(
        existing_role, role.dict(skip_defaults=True))
    data = CRUD.update(db, "roles", role_id,
                       updated_role)
    return Role(**data)


def delete_role(role_id: str, db):
    resp = CRUD.delete(db, "roles", role_id)
    return resp


@routes.post("/roles", response_model=Role)
def create_role_api(role: RoleCreate, db=Depends(get_db)):
    role = create_role(role, db)
    return role


@routes.get("/roles", response_model=List[Role])
def get_roles_api(db=Depends(get_db),
                  skip: int = 0,
                  limit: int = 25,
                  search: str = None,
                  sort: List[str] = Query([], alias="sort_by")):
    roles = get_roles(
        db=db, skip=skip, limit=limit, search=search, sort=sort)
    return roles


@routes.get("/roles/{role_id}", response_model=Role)
def get_role_api(role_id: str, db=Depends(get_db)):
    role = get_role(role_id, db)
    return role


@routes.put("/roles/{role_id}", response_model=Role)
def update_role_api(role_id: str, role: RoleCreate, response: Response, db=Depends(get_db)):
    try:
        update_role(role_id, role, db)
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to update %s record" % role_id))


@routes.patch("/roles/{role_id}", response_model=Role)
def partial_update_role_api(role_id: str, role: RolePartial, db=Depends(get_db)):
    updated_role = partial_update_role(
        role_id, role, db)
    return updated_role


@routes.delete("/roles/{role_id}")
def delete_role_api(role_id: str, response: Response, db=Depends(get_db)):
    try:
        delete_role(role_id, db)
        response.status_code = HTTP_204_NO_CONTENT
        return JSONResponse(dict(message="Role %s deleted successfully." % role_id))
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to delete Role %s." % role_id))
