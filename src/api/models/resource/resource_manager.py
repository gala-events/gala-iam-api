from models.base_record_manager import BaseRecordManager
from models.resource.resource_model import Resource, RESOURCE_MODEL_NAME


class ResourceManager(BaseRecordManager):
    """ResourceManager to handle CRUD functionality"""

    model = Resource
    model_name = RESOURCE_MODEL_NAME
