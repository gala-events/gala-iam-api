from models.base_record_manager import BaseRecordManager
from models.user.user_model import User, USER_MODEL_NAME


class UserManager(BaseRecordManager):
    """UserManager to handle CRUD functionality"""

    model = User
    model_name = USER_MODEL_NAME
