import os
from starlette.requests import Request


def get_db(request: Request):
    db_name = os.environ.get("DB_NAME", "GALA_IAM_DB")
    return request.state.db.connection[db_name]
