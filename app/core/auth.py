import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.core.settings import settings

security = HTTPBasic()


def basic_auth_dependency(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, settings.admin_user)
    correct_password = secrets.compare_digest(credentials.password, settings.admin_pass)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Auth requise",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
