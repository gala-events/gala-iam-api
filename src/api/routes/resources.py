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
from models import Resource, ResourceCreate, ResourceManager, ResourcePartial
from utils import get_db, json_merge_patch
from utils.exceptions import RecordNotFoundException

routes = APIRouter()


@routes.post("/resources", response_model=Resource)
def create_resource_api(resource: ResourceCreate, response: Response, db=Depends(get_db)):
    try:
        new_resource = ResourceManager.create(db, resource)
        response.status_code = HTTP_201_CREATED
        return new_resource
    except ValidationError:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to create resource"))


@routes.get("/resources", response_model=List[Resource])
def get_resources_api(response: Response,
                      db=Depends(get_db),
                      skip: int = 0,
                      limit: int = 25,
                      search: str = None,
                      sort: List[str] = Query([], alias="sort_by")):
    try:
        response.status_code = HTTP_200_OK
        resources = ResourceManager.find(db, skip=skip, limit=limit,
                                         search=search, sort=sort)
        return resources
    except Exception as exc:
        response.status_code = HTTP_500_INTERNAL_SERVER_ERROR
        return JSONResponse(dict(error="Failed to get resources. %s" % str(exc)))


@routes.get("/resources/{resource_id}", response_model=Resource)
def get_resource_api(resource_id: str, response: Response, db=Depends(get_db)):
    try:
        resource = ResourceManager.find_by_uuid(db, resource_id)
        return resource
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))


@routes.put("/resources/{resource_id}", response_model=Resource)
def update_resource_api(resource_id: str, resource: ResourceCreate, response: Response, db=Depends(get_db)):
    try:
        updated_resource = ResourceManager.update(db, resource_id, resource)
        return updated_resource
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except ValidationError as exc:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to update %s resource. %s" % (resource_id, str(exc))))


@routes.patch("/resources/{resource_id}", response_model=Resource)
def partial_update_resource_api(resource_id: str, resource: ResourcePartial, response: Response, db=Depends(get_db)):
    try:
        updated_resource = ResourceManager.partial_update(
            db, resource_id, resource)
        response.status_code = HTTP_200_OK
        return updated_resource
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except ValidationError as exc:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to update %s resource. %s" % (resource_id, str(exc))))


@routes.delete("/resources/{resource_id}")
def delete_resource_api(resource_id: str, response: Response, db=Depends(get_db)):
    try:
        ResourceManager.delete(db, resource_id)
        response.status_code = HTTP_204_NO_CONTENT
        return JSONResponse(dict(message="Resource %s deleted successfully." % resource_id))
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
