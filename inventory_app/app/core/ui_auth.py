from fastapi import Request
from fastapi.responses import RedirectResponse
from jose import JWTError

from app.core.security import decode_access_token


def require_ui_user(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        return RedirectResponse("/ui/login", status_code=302)

    try:
        user_id = decode_access_token(token)
        request.state.user_id = user_id
    except JWTError:
        return RedirectResponse("/ui/login", status_code=302)
