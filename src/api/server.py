import os

from fastapi import Depends, FastAPI
from pymongo import MongoClient
from starlette.requests import Request
from starlette.responses import Response

from db import Database
from routes import permissions, roles, service_accounts, user_groups, users
from utils import get_db

MONGO_DB__HOST_URI = os.environ.get("MONGO_DB__HOST_URI", "localhost")
MONGO_DB__HOST_PORT = int(os.environ.get("MONGO_DB__HOST_PORT", 27017))
db_connection = MongoClient(host=MONGO_DB__HOST_URI, port=MONGO_DB__HOST_PORT)

app = FastAPI(title="GALA Authorization Management API",
              description="Authorization Management module for managing authorization on GALA resources",
              openapi_url="/gala_authz_api__openapi.json",
              version="v1")


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = Database(db_connection)
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response

app.include_router(roles.routes, tags=["CRUD on Roles"])
app.include_router(permissions.routes, tags=["CRUD on Permissions"])
app.include_router(users.routes, tags=["CRUD on Users"])
app.include_router(service_accounts.routes, tags=["CRUD on Service Accounts"])
app.include_router(user_groups.routes, tags=["CRUD on User Groups"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
