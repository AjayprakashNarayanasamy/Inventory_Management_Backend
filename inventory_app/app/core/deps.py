from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

from app.core.security import decode_access_token

# This tells FastAPI / Swagger that we use Bearer tokens
security = HTTPBearer()


def require_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """
    Extract JWT token from:
    Authorization: Bearer <token>
    """
    try:
        token = credentials.credentials
        user_id = decode_access_token(token)
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
