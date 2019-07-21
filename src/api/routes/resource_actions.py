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
from models import ResourceAction, ResourceActionCreate, ResourceActionManager, ResourceActionPartial
from utils import get_db, json_merge_patch
from utils.exceptions import RecordNotFoundException

routes = APIRouter()


@routes.post("/resource_actions", response_model=ResourceAction)
def create_resource_action_api(resource_action: ResourceActionCreate, response: Response, db=Depends(get_db)):
    try:
        new_resource_action = ResourceActionManager.create(db, resource_action)
        response.status_code = HTTP_201_CREATED
        return new_resource_action
    except ValidationError:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to create resource_action"))


@routes.get("/resource_actions", response_model=List[ResourceAction])
def get_resource_actions_api(response: Response,
                             db=Depends(get_db),
                             skip: int = 0,
                             limit: int = 25,
                             search: str = None,
                             sort: List[str] = Query([], alias="sort_by")):
    try:
        response.status_code = HTTP_200_OK
        resource_actions = ResourceActionManager.find(db, skip=skip, limit=limit,
                                                      search=search, sort=sort)
        return resource_actions
    except Exception as exc:
        response.status_code = HTTP_500_INTERNAL_SERVER_ERROR
        return JSONResponse(dict(error="Failed to get resource_actions. %s" % str(exc)))


@routes.get("/resource_actions/{resource_action_id}", response_model=ResourceAction)
def get_resource_action_api(resource_action_id: str, response: Response, db=Depends(get_db)):
    try:
        resource_action = ResourceActionManager.find_by_uuid(
            db, resource_action_id)
        return resource_action
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))


@routes.put("/resource_actions/{resource_action_id}", response_model=ResourceAction)
def update_resource_action_api(resource_action_id: str, resource_action: ResourceActionCreate, response: Response, db=Depends(get_db)):
    try:
        updated_resource_action = ResourceActionManager.update(
            db, resource_action_id, resource_action)
        return updated_resource_action
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except ValidationError as exc:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to update %s resource_action. %s" % (resource_action_id, str(exc))))


@routes.patch("/resource_actions/{resource_action_id}", response_model=ResourceAction)
def partial_update_resource_action_api(resource_action_id: str, resource_action: ResourceActionPartial, response: Response, db=Depends(get_db)):
    try:
        updated_resource_action = ResourceActionManager.partial_update(
            db, resource_action_id, resource_action)
        response.status_code = HTTP_200_OK
        return updated_resource_action
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except ValidationError as exc:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to update %s resource_action. %s" % (resource_action_id, str(exc))))


@routes.delete("/resource_actions/{resource_action_id}")
def delete_resource_action_api(resource_action_id: str, response: Response, db=Depends(get_db)):
    try:
        ResourceActionManager.delete(db, resource_action_id)
        response.status_code = HTTP_204_NO_CONTENT
        return JSONResponse(dict(message="ResourceAction %s deleted successfully." % resource_action_id))
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
