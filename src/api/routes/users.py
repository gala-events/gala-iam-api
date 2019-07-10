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
from models import User, UserCreate, UserPartial
from utils import get_db, json_merge_patch
from utils.exceptions import RecordNotFoundException

routes = APIRouter()


@routes.post("/users", response_model=User)
def create_user(user: UserCreate, db=Depends(get_db)):
    user_id = CRUD.create(db, "users", user.dict())
    user_record = CRUD.find_by_uuid(db, "users", str(user_id))
    user = User(**user_record)
    return user


@routes.get("/users", response_model=List[User])
def get_users(db=Depends(get_db),
              skip: int = 0,
              limit: int = 25,
              search: str = None,
              sort: List[str] = Query([], alias="sort_by")):
    filter_params = dict()
    search_fields = ["uuid", "name"]
    if search:
        map(lambda search_field: filter_params.update(
            search_field=re.compile(search)), search_fields)

    data = CRUD.find(db, "users", skip=skip,
                     limit=limit,
                     filter_params=filter_params,
                     sort=sort)
    return [User(**d) for d in data]


@routes.get("/users/{user_id}", response_model=User)
def get_user(user_id: str, db=Depends(get_db)):
    data = CRUD.find_by_uuid(db, "users", user_id)
    return User(**data)


@routes.put("/users/{user_id}", response_model=User)
def update_user(user_id: str, user: UserCreate, response: Response, db=Depends(get_db)):
    try:
        data = CRUD.update(db, "users", user_id, user.dict())
        return User(**data)
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to update %s record" % user_id))


@routes.patch("/users/{user_id}", response_model=User)
def partial_update_user(user_id: str, user: UserPartial, db=Depends(get_db)):
    existing_user = CRUD.find_by_uuid(db, "users", user_id)
    updated_user = json_merge_patch(
        existing_user, user.dict(skip_defaults=True))
    data = CRUD.update(db, "users", user_id, updated_user)
    return User(**data)


@routes.delete("/users/{user_id}")
def delete_user(user_id: str, response: Response, db=Depends(get_db)):
    try:
        CRUD.delete(db, "users", user_id)
        response.status_code = HTTP_204_NO_CONTENT
        return JSONResponse(dict(message="Event %s deleted successfully." % user_id))
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to delete Event %s." % user_id))
