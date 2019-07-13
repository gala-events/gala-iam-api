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
from models import Resource, ResourceCreate, ResourcePartial
from utils import get_db, json_merge_patch
from utils.exceptions import RecordNotFoundException

routes = APIRouter()


def create_resource(resource: ResourceCreate, db: Database):
    resource_data = resource.dict()
    resource_id = CRUD.create(db, "resources", resource_data)
    resource_record = CRUD.find_by_uuid(
        db, "resources", str(resource_id))
    resource = Resource(**resource_record)
    return resource


def get_resources(db,
                  skip: int = 0,
                  limit: int = 25,
                  search: str = None,
                  sort: List[str] = None):
    filter_params = dict()
    search_fields = ["uuid", "name"]
    if search:
        map(lambda search_field: filter_params.update(
            search_field=re.compile(search)), search_fields)

    data = CRUD.find(db, "resources", skip=skip,
                     limit=limit,
                     filter_params=filter_params,
                     sort=sort)
    return [Resource(**d) for d in data]


def get_resource(resource_id: str, db):
    data = CRUD.find_by_uuid(db, "resources", resource_id)
    return Resource(**data)


def get_resource_by_name(name: str, db):
    data = get_resources(db, search=name)
    if len(data) == 0:
        raise ValueError("Resource not found with name [%s]", name)
    if len(data) > 1:
        raise ValueError("Multiple Resources found with name [%s]", name)
    return data[0]


def update_resource(resource_id: str, resource: ResourceCreate, db):
    data = CRUD.update(db, "resources",
                       resource_id, resource.dict())
    return Resource(**data)


def partial_update_resource(resource_id: str, resource: ResourcePartial, db):
    existing_resource = CRUD.find_by_uuid(
        db, "resources", resource_id)
    updated_resource = json_merge_patch(
        existing_resource, resource.dict(skip_defaults=True))
    data = CRUD.update(db, "resources", resource_id,
                       updated_resource)
    return Resource(**data)


def delete_resource(resource_id: str, db):
    resp = CRUD.delete(db, "resources", resource_id)
    return resp


@routes.post("/resources", response_model=Resource)
def create_resource_api(resource: ResourceCreate, db=Depends(get_db)):
    resource = create_resource(resource, db)
    return resource


@routes.get("/resources", response_model=List[Resource])
def get_resources_api(db=Depends(get_db),
                      skip: int = 0,
                      limit: int = 25,
                      search: str = None,
                      sort: List[str] = Query([], alias="sort_by")):
    resources = get_resources(
        db=db, skip=skip, limit=limit, search=search, sort=sort)
    return resources


@routes.get("/resources/{resource_id}", response_model=Resource)
def get_resource_api(resource_id: str, db=Depends(get_db)):
    resource = get_resource(resource_id, db)
    return resource


@routes.put("/resources/{resource_id}", response_model=Resource)
def update_resource_api(resource_id: str, resource: ResourceCreate, response: Response, db=Depends(get_db)):
    try:
        update_resource(resource_id, resource, db)
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to update %s record" % resource_id))


@routes.patch("/resources/{resource_id}", response_model=Resource)
def partial_update_resource_api(resource_id: str, resource: ResourcePartial, db=Depends(get_db)):
    updated_resource = partial_update_resource(
        resource_id, resource, db)
    return updated_resource


@routes.delete("/resources/{resource_id}")
def delete_resource_api(resource_id: str, response: Response, db=Depends(get_db)):
    try:
        delete_resource(resource_id, db)
        response.status_code = HTTP_204_NO_CONTENT
        return JSONResponse(dict(message="Resource %s deleted successfully." % resource_id))
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to delete Resource %s." % resource_id))
