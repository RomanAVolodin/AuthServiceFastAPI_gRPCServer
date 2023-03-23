from functools import lru_cache

from async_fastapi_jwt_auth import AuthJWT

from core.settings import settings
from db import redis_db


class AuthService:
    async def revoke_both_tokens(self, authorize: AuthJWT):
        refresh_jti = (await authorize.get_raw_jwt())['jti']
        access_jti = (await authorize.get_raw_jwt())['access_jti']
        await redis_db.redis.setex(access_jti, settings.access_token_expires_seconds, 'true')
        await redis_db.redis.setex(refresh_jti, settings.refresh_token_expires_seconds, 'true')


@lru_cache()
def get_auth_service() -> AuthService:
    return AuthService()
