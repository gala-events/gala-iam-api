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
from models import ResourceAction, ResourceActionCreate, ResourceActionPartial
from utils import get_db, json_merge_patch
from utils.exceptions import RecordNotFoundException

routes = APIRouter()


def create_resource_action(resource_action: ResourceActionCreate, db: Database):
    resource_action_data = resource_action.dict()
    resource_action_id = CRUD.create(
        db, "resource_actions", resource_action_data)
    resource_action_record = CRUD.find_by_uuid(
        db, "resource_actions", str(resource_action_id))
    resource_action = ResourceAction(**resource_action_record)
    return resource_action


def get_resource_actions(db,
                         skip: int = 0,
                         limit: int = 25,
                         search: str = None,
                         sort: List[str] = None):
    filter_params = dict()
    search_fields = ["uuid", "name"]
    if search:
        map(lambda search_field: filter_params.update(
            search_field=re.compile(search)), search_fields)

    data = CRUD.find(db, "resource_actions", skip=skip,
                     limit=limit,
                     filter_params=filter_params,
                     sort=sort)
    return [ResourceAction(**d) for d in data]


def get_resource_action(resource_action_id: str, db):
    data = CRUD.find_by_uuid(db, "resource_actions", resource_action_id)
    return ResourceAction(**data)


def get_resource_action_by_name(name: str, db):
    data = get_resource_actions(db, search=name)
    if len(data) == 0:
        raise ValueError("ResourceAction not found with name [%s]", name)
    if len(data) > 1:
        raise ValueError("Multiple ResourceActions found with name [%s]", name)
    return data[0]


def update_resource_action(resource_action_id: str, resource_action: ResourceActionCreate, db):
    data = CRUD.update(db, "resource_actions",
                       resource_action_id, resource_action.dict())
    return ResourceAction(**data)


def partial_update_resource_action(resource_action_id: str, resource_action: ResourceActionPartial, db):
    existing_resource_action = CRUD.find_by_uuid(
        db, "resource_actions", resource_action_id)
    updated_resource_action = json_merge_patch(
        existing_resource_action, resource_action.dict(skip_defaults=True))
    data = CRUD.update(db, "resource_actions", resource_action_id,
                       updated_resource_action)
    return ResourceAction(**data)


def delete_resource_action(resource_action_id: str, db):
    resp = CRUD.delete(db, "resource_actions", resource_action_id)
    return resp


@routes.post("/resource_actions", response_model=ResourceAction)
def create_resource_action_api(resource_action: ResourceActionCreate, db=Depends(get_db)):
    resource_action = create_resource_action(resource_action, db)
    return resource_action


@routes.get("/resource_actions", response_model=List[ResourceAction])
def get_resource_actions_api(db=Depends(get_db),
                             skip: int = 0,
                             limit: int = 25,
                             search: str = None,
                             sort: List[str] = Query([], alias="sort_by")):
    resource_actions = get_resource_actions(
        db=db, skip=skip, limit=limit, search=search, sort=sort)
    return resource_actions


@routes.get("/resource_actions/{resource_action_id}", response_model=ResourceAction)
def get_resource_action_api(resource_action_id: str, db=Depends(get_db)):
    resource_action = get_resource_action(resource_action_id, db)
    return resource_action


@routes.put("/resource_actions/{resource_action_id}", response_model=ResourceAction)
def update_resource_action_api(resource_action_id: str, resource_action: ResourceActionCreate, response: Response, db=Depends(get_db)):
    try:
        update_resource_action(resource_action_id, resource_action, db)
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to update %s record" % resource_action_id))


@routes.patch("/resource_actions/{resource_action_id}", response_model=ResourceAction)
def partial_update_resource_action_api(resource_action_id: str, resource_action: ResourceActionPartial, db=Depends(get_db)):
    updated_resource_action = partial_update_resource_action(
        resource_action_id, resource_action, db)
    return updated_resource_action


@routes.delete("/resource_actions/{resource_action_id}")
def delete_resource_action_api(resource_action_id: str, response: Response, db=Depends(get_db)):
    try:
        delete_resource_action(resource_action_id, db)
        response.status_code = HTTP_204_NO_CONTENT
        return JSONResponse(dict(message="ResourceAction %s deleted successfully." % resource_action_id))
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to delete ResourceAction %s." % resource_action_id))
