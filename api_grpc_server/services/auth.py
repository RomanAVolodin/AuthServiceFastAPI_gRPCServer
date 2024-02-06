from functools import lru_cache

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.settings import settings
from db import redis_db
from models.user import User
from schemas.login_history import LoginHistoryCreateDto
from schemas.user import UserDataInToken
from services.login_history_repository import history_crud


class AuthService:
    async def revoke_both_tokens(self, authorize: AuthJWT) -> None:
        refresh_jti = (await authorize.get_raw_jwt())['jti']
        access_jti = (await authorize.get_raw_jwt())['access_jti']
        await redis_db.redis.setex(access_jti, settings.access_token_expires_seconds, 'true')
        await redis_db.redis.setex(refresh_jti, settings.refresh_token_expires_seconds, 'true')

    async def generate_tokens(
        self, request: Request, db: AsyncSession, authorize: AuthJWT, user: User
    ) -> dict[str, str]:
        access_token = await authorize.create_access_token(
            subject=str(user.id), user_claims=UserDataInToken.from_orm(user).dict()
        )
        access_jti = await authorize.get_jti(access_token)
        refresh_token = await authorize.create_refresh_token(
            subject=str(user.id), user_claims={'access_jti': access_jti}
        )
        refresh_jti = await authorize.get_jti(refresh_token)

        history = LoginHistoryCreateDto(
            user_id=user.id,
            user_agent=request.headers.get('User-Agent'),
            user_ip=request.client.host,
            access_token=access_jti,
            refresh_token=refresh_jti,
            user_device_type='web',
        )

        await history_crud.create(
            db=db,
            obj_in=history,
        )
        return {'access_token': access_token, 'refresh_token': refresh_token}


@lru_cache()
def get_auth_service() -> AuthService:
    return AuthService()
