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
from models import Role, RoleCreate
from models.role import RolePartial
from utils import get_db, json_merge_patch
from utils.exceptions import RecordNotFoundException

routes = APIRouter()


@routes.post("/roles", response_model=Role)
def create_role(role: RoleCreate, db=Depends(get_db)):
    role_id = CRUD.create(db, "roles", role.dict())
    role_record = CRUD.find_by_uuid(db, "roles", str(role_id))
    role = Role(**role_record)
    return role


@routes.get("/roles", response_model=List[Role])
def get_roles(db=Depends(get_db),
              skip: int = 0,
              limit: int = 25,
              search: str = None,
              sort: List[str] = Query([], alias="sort_by")):
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


@routes.get("/roles/{role_id}", response_model=Role)
def get_role(role_id: str, db=Depends(get_db)):
    data = CRUD.find_by_uuid(db, "roles", role_id)
    return Role(**data)


@routes.put("/roles/{role_id}", response_model=Role)
def update_role(role_id: str, role: RoleCreate, response: Response, db=Depends(get_db)):
    try:
        data = CRUD.update(db, "roles", role_id, role.dict())
        return Role(**data)
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to update %s record" % role_id))


@routes.patch("/roles/{role_id}", response_model=RolePartial)
def partial_update_role(role_id: str, role: BaseModel, db=Depends(get_db)):
    existing_role = CRUD.find_by_uuid(db, "roles", role_id)
    updated_role = json_merge_patch(
        existing_role, role.dict(skip_defaults=True))
    data = CRUD.update(db, "roles", role_id, updated_role)
    return Role(**data)


@routes.delete("/roles/{role_id}")
def delete_role(role_id: str, response: Response, db=Depends(get_db)):
    try:
        CRUD.delete(db, "roles", role_id)
        response.status_code = HTTP_204_NO_CONTENT
        return JSONResponse(dict(message="Event %s deleted successfully." % role_id))
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to delete Event %s." % role_id))
