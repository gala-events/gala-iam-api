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
from models import UserGroup, UserGroupCreate, UserGroupPartial
from utils import get_db, json_merge_patch
from utils.exceptions import RecordNotFoundException

routes = APIRouter()


@routes.post("/user_groups", response_model=UserGroup)
def create_user_group(user_group: UserGroupCreate, db=Depends(get_db)):
    user_group_id = CRUD.create(db, "user_groups", user_group.dict())
    user_group_record = CRUD.find_by_uuid(
        db, "user_groups", str(user_group_id))
    user_group = UserGroup(**user_group_record)
    return user_group


@routes.get("/user_groups", response_model=List[UserGroup])
def get_user_groups(db=Depends(get_db),
                    skip: int = 0,
                    limit: int = 25,
                    search: str = None,
                    sort: List[str] = Query([], alias="sort_by")):
    filter_params = dict()
    search_fields = ["uuid", "name"]
    if search:
        map(lambda search_field: filter_params.update(
            search_field=re.compile(search)), search_fields)

    data = CRUD.find(db, "user_groups", skip=skip,
                     limit=limit,
                     filter_params=filter_params,
                     sort=sort)
    return [UserGroup(**d) for d in data]


@routes.get("/user_groups/{user_group_id}", response_model=UserGroup)
def get_user_group(user_group_id: str, db=Depends(get_db)):
    data = CRUD.find_by_uuid(db, "user_groups", user_group_id)
    return UserGroup(**data)


@routes.put("/user_groups/{user_group_id}", response_model=UserGroup)
def update_user_group(user_group_id: str, user_group: UserGroupCreate, response: Response, db=Depends(get_db)):
    try:
        data = CRUD.update(db, "user_groups", user_group_id, user_group.dict())
        return UserGroup(**data)
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to update %s record" % user_group_id))


@routes.patch("/user_groups/{user_group_id}", response_model=UserGroup)
def partial_update_user_group(user_group_id: str, user_group: UserGroupPartial, db=Depends(get_db)):
    existing_user_group = CRUD.find_by_uuid(db, "user_groups", user_group_id)
    updated_user_group = json_merge_patch(
        existing_user_group, user_group.dict(skip_defaults=True))
    data = CRUD.update(db, "user_groups", user_group_id, updated_user_group)
    return UserGroup(**data)


@routes.delete("/user_groups/{user_group_id}")
def delete_user_group(user_group_id: str, response: Response, db=Depends(get_db)):
    try:
        CRUD.delete(db, "user_groups", user_group_id)
        response.status_code = HTTP_204_NO_CONTENT
        return JSONResponse(dict(message="Event %s deleted successfully." % user_group_id))
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to delete Event %s." % user_group_id))
