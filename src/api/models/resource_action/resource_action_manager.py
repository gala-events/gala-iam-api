from models.base_record_manager import BaseRecordManager
from models.resource_action.resource_action_model import ResourceAction, RESOURCE_ACTION_MODEL_NAME


class ResourceActionManager(BaseRecordManager):
    """ResourceActionManager to handle CRUD functionality"""

    model = ResourceAction
    model_name = RESOURCE_ACTION_MODEL_NAME
