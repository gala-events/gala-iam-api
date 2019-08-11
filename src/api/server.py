import os

from fastapi import Depends, FastAPI
from pymongo import MongoClient
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from db import Database
from routes import (groups, permissions, resource_actions, resources, roles,
                    service_accounts, auth, users)
from utils import get_db

MONGO_DB__HOST_URI = os.environ.get("MONGO_DB__HOST_URI", "localhost")
MONGO_DB__HOST_PORT = int(os.environ.get("MONGO_DB__HOST_PORT", 27017))
IAM__API_SECRET_KEY = os.environ.get(
    "IAM__API_SECRET_KEY", "iam__api_secret_key")
db_connection = MongoClient(host=MONGO_DB__HOST_URI, port=MONGO_DB__HOST_PORT)

app = FastAPI(title="GALA Identity and Access Management API",
              description="Authentication and Authorization Management module for GALA resources",
              openapi_url="/gala_iam_api__openapi.json")


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error",
                        status_code=HTTP_500_INTERNAL_SERVER_ERROR)
    try:
        request.state.db = Database(db_connection)
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response

# app.include_router(roles.routes, tags=["RolesManager"])
# app.include_router(resources.routes, tags=["ResourcesManager"])
# app.include_router(resource_actions.routes, tags=[
#                    "ResourceActionsManager"])
# app.include_router(permissions.routes, tags=["PermissionsManager"])
# app.include_router(users.routes, tags=["UsersManager"])
# app.include_router(service_accounts.routes, tags=["Service AccountsManager"])
# app.include_router(groups.routes, tags=["GroupsManager"])
app.include_router(auth.routes, tags=["TokenManager"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=80, log_level="debug", reload=True)
