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
from models import Group, GroupCreate, GroupManager, GroupPartial
from utils import get_db, json_merge_patch
from utils.exceptions import RecordNotFoundException

routes = APIRouter()


@routes.post("/groups", response_model=Group)
def create_group_api(group: GroupCreate, response: Response, db=Depends(get_db)):
    try:
        new_group = GroupManager.create(db, group)
        response.status_code = HTTP_201_CREATED
        return new_group
    except ValidationError as exc:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse({"error": "Failed to create group: %s" % exc.raw_errors})
    except Exception as exc:
        response.status_code = HTTP_500_INTERNAL_SERVER_ERROR
        return JSONResponse({"error": "Failed to create group: %s" % str(exc.args)})


@routes.get("/groups", response_model=List[Group])
def get_groups_api(response: Response,
                   db=Depends(get_db),
                   skip: int = 0,
                   limit: int = 25,
                   search: str = None,
                   sort: List[str] = Query([], alias="sort_by")):
    try:
        response.status_code = HTTP_200_OK
        groups = GroupManager.find(db, skip=skip, limit=limit,
                                   search=search, sort=sort)
        return groups
    except Exception as exc:
        response.status_code = HTTP_500_INTERNAL_SERVER_ERROR
        return JSONResponse(dict(error="Failed to get groups. %s" % str(exc)))


@routes.get("/groups/{group_id}", response_model=Group)
def get_group_api(group_id: str, response: Response, db=Depends(get_db)):
    try:
        group = GroupManager.find_by_uuid(db, group_id)
        return group
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))


@routes.put("/groups/{group_id}", response_model=Group)
def update_group_api(group_id: str, group: GroupCreate, response: Response, db=Depends(get_db)):
    try:
        updated_group = GroupManager.update(db, group_id, group)
        return updated_group
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except ValidationError as exc:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to update %s group. %s" % (group_id, str(exc))))


@routes.patch("/groups/{group_id}", response_model=Group)
def partial_update_group_api(group_id: str, group: GroupPartial, response: Response, db=Depends(get_db)):
    try:
        updated_group = GroupManager.partial_update(db, group_id, group)
        response.status_code = HTTP_200_OK
        return updated_group
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except ValidationError as exc:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to update %s group. %s" % (group_id, str(exc))))


@routes.delete("/groups/{group_id}")
def delete_group_api(group_id: str, response: Response, db=Depends(get_db)):
    try:
        GroupManager.delete(db, group_id)
        response.status_code = HTTP_204_NO_CONTENT
        return JSONResponse(dict(message="Group %s deleted successfully." % group_id))
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
