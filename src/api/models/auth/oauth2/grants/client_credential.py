from db.crud import CRUD
from models.service_account.service_account_manager import ServiceAccountManager
from models.service_account.service_account_model import ServiceAccount, ServiceAccountPostCreate
from utils.auth import verify_hash


class ClientCredentialGrantManager:
    """Manager that handles Client Credential Grant Flow for Oauth2
    """
    manager = ServiceAccountManager
    model = ServiceAccountPostCreate

    @classmethod
    def get_service_account_with_credentials(cls, db, client_id: str, client_secret: str):
        """Get the service account with the provided client credentials

        Arguments:
            db {Database} -- a live Database connection
            client_id {str} -- Client Unique Id
            client_secret {str} -- Client password or secret

        Returns:
            Union[ServiceAccountPostCreate, None] -- Returns the service account which exists with the credentials
        """
        existing_service_accounts = CRUD.find(db, cls.manager.model_name, filter_params={
            "client_id": client_id})

        if len(existing_service_accounts) == 1:
            existing_service_account = ServiceAccountPostCreate(**existing_service_accounts[0])
            if verify_hash(client_secret, existing_service_account.client_secret):
                return existing_service_account

        return None

    @classmethod
    def authenticate(cls, db, client_id: str, client_secret: str, *args, **kwargs):
        """Authenticates the service account

        Arguments:
            db {Database} -- a live Database connection
            client_id {str} -- Client Unique Id
            client_secret {str} -- Client password or secret

        Returns:
            Union[ServiceAccountPostCreate, None] -- Returns the service account which exists with the credentials
        """
        service_account = cls.get_service_account_with_credentials(
            db, client_id, client_secret)
        if not service_account:
            return False
        return ServiceAccount(**service_account.dict())
