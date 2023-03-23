from functools import wraps

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, Request, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_session
from helpers.auth_request import AuthRequest
from helpers.exceptions import AuthException
from models.user import UserRole
from schemas.user import UserInDb
from services.user_repository import users_crud


def roles_required(roles_list: list[UserRole]):
    def decorator(function):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            user: UserInDb = kwargs.get('request').custom_user
            if not user or user.role not in [x.value for x in roles_list]:
                raise AuthException('This operation is forbidden for you', status_code=status.HTTP_403_FORBIDDEN)
            return await function(*args, **kwargs)

        return wrapper

    return decorator


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request, db: AsyncSession = Depends(get_session)) -> UserInDb | None:
        authorize = AuthJWT(req=request)
        await authorize.jwt_optional()
        user_id = await authorize.get_jwt_subject()
        if not user_id:
            return None
        user = await users_crud.get(db=db, id=user_id)
        return UserInDb.from_orm(user)


async def get_current_user_global(request: AuthRequest, user: AsyncSession = Depends(JWTBearer())):
    request.custom_user = user
