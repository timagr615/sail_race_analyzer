from fastapi import Depends, HTTPException
from app.users.schemas import UserDisplay
from app.auth.jwt import get_current_user


class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self._allowed_roles = allowed_roles

    def __call__(self, user: UserDisplay = Depends(get_current_user)):
        if user.role not in self._allowed_roles:
            raise HTTPException(status_code=403, detail="Operation not permitted")


allow_view = RoleChecker(['guest', 'user', 'staff', 'admin', 'superuser'])
allow_add_news = RoleChecker(['staff', 'admin', 'superuser'])
allow_update = RoleChecker(['admin', 'superuser'])
allow_create_admins = RoleChecker(['superuser'])
