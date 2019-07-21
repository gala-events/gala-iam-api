from models.base_record_manager import BaseRecordManager
from models.role.role_model import Role, ROLE_MODEL_NAME


class RoleManager(BaseRecordManager):
    """RoleManager to handle CRUD functionality"""

    model = Role
    model_name = ROLE_MODEL_NAME
