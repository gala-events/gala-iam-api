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
from models import User, UserCreate, UserManager, UserPartial
from utils import get_db, json_merge_patch
from utils.exceptions import RecordNotFoundException

routes = APIRouter()


@routes.post("/users", response_model=User)
def create_user_api(user: UserCreate, response: Response, db=Depends(get_db)):
    try:
        new_user = UserManager.create(db, user)
        response.status_code = HTTP_201_CREATED
        return new_user
    except ValidationError:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to create user"))


@routes.get("/users", response_model=List[User])
def get_users_api(response: Response,
                  db=Depends(get_db),
                  skip: int = 0,
                  limit: int = 25,
                  search: str = None,
                  sort: List[str] = Query([], alias="sort_by")):
    try:
        response.status_code = HTTP_200_OK
        users = UserManager.find(db, skip=skip, limit=limit,
                                 search=search, sort=sort)
        return users
    except Exception as exc:
        response.status_code = HTTP_500_INTERNAL_SERVER_ERROR
        return JSONResponse(dict(error="Failed to get users. %s" % str(exc)))


@routes.get("/users/{user_id}", response_model=User)
def get_user_api(user_id: str, response: Response, db=Depends(get_db)):
    try:
        user = UserManager.find_by_uuid(db, user_id)
        return user
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))


@routes.put("/users/{user_id}", response_model=User)
def update_user_api(user_id: str, user: UserCreate, response: Response, db=Depends(get_db)):
    try:
        updated_user = UserManager.update(db, user_id, user)
        return updated_user
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except ValidationError as exc:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to update %s user. %s" % (user_id, str(exc.raw_errors))))


@routes.patch("/users/{user_id}", response_model=User)
def partial_update_user_api(user_id: str, user: UserPartial, response: Response, db=Depends(get_db)):
    try:
        updated_user = UserManager.partial_update(db, user_id, user)
        response.status_code = HTTP_200_OK
        return updated_user
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
    except ValidationError as exc:
        response.status_code = HTTP_400_BAD_REQUEST
        return JSONResponse(dict(error="Failed to update %s user. %s" % (user_id, str(exc.raw_errors))))


@routes.delete("/users/{user_id}")
def delete_user_api(user_id: str, response: Response, db=Depends(get_db)):
    try:
        UserManager.delete(db, user_id)
        response.status_code = HTTP_204_NO_CONTENT
        return JSONResponse(dict(message="User %s deleted successfully." % user_id))
    except RecordNotFoundException as exc:
        response.status_code = HTTP_404_NOT_FOUND
        return JSONResponse(dict(error=str(exc)))
