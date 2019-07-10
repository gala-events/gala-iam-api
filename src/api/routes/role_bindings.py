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
from models import RoleBinding, RoleBindingCreate, RoleBindingPartial
from utils import get_db, json_merge_patch
from utils.exceptions import RecordNotFoundException

routes = APIRouter()


@routes.post("/role_bindings", response_model=RoleBinding)
def create_role_binding(role_binding: RoleBindingCreate, db=Depends(get_db)):
    role_binding_id = CRUD.create(db, "role_bindings", role_binding.dict())
    role_binding_record = CRUD.find_by_uuid(
        db, "role_bindings", str(role_binding_id))
    role_binding = RoleBinding(**role_binding_record)
    return role_binding


@routes.get("/role_bindings", response_model=List[RoleBinding])
def get_role_bindings(db=Depends(get_db),
                      skip: int = 0,
                      limit: int = 25,
                      search: str = None,
                      sort: List[str] = Query([], alias="sort_by")):
    filter_params = dict()
    search_fields = ["uuid", "name"]
    if search:
        map(lambda search_field: filter_params.update(
            search_field=re.compile(search)), search_fields)

    data = CRUD.find(db, "role_bindings", skip=skip,
                     limit=limit,
                     filter_params=filter_params,
                     sort=sort)
    return [RoleBinding(**d) for d in data]


@routes.get("/role_bindings/{role_binding_id}", response_model=RoleBinding)
def get_role_binding(role_binding_id: str, db=Depends(get_db)):
    data = CRUD.find_by_uuid(db, "role_bindings", role_binding_id)
    return RoleBinding(**data)


@routes.put("/role_bindings/{role_binding_id}", response_model=RoleBinding)
def update_role_binding(role_binding_id: str, role_binding: RoleBindingCreate, response: Response, db=Depends(get_db)):
    try:
        data = CRUD.update(db, "role_bindings",
                           role_binding_id, role_binding.dict())
        return RoleBinding(**data)
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to update %s record" % role_binding_id))


@routes.patch("/role_bindings/{role_binding_id}", response_model=RoleBinding)
def partial_update_role_binding(role_binding_id: str, role_binding: RoleBindingPartial, db=Depends(get_db)):
    existing_role_binding = CRUD.find_by_uuid(
        db, "role_bindings", role_binding_id)
    updated_role_binding = json_merge_patch(
        existing_role_binding, role_binding.dict(skip_defaults=True))
    data = CRUD.update(db, "role_bindings", role_binding_id,
                       updated_role_binding)
    return RoleBinding(**data)


@routes.delete("/role_bindings/{role_binding_id}")
def delete_role_binding(role_binding_id: str, response: Response, db=Depends(get_db)):
    try:
        CRUD.delete(db, "role_bindings", role_binding_id)
        response.status_code = HTTP_204_NO_CONTENT
        return JSONResponse(dict(message="Event %s deleted successfully." % role_binding_id))
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to delete Event %s." % role_binding_id))
