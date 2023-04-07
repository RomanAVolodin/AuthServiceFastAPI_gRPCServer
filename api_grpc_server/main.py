import logging

import uvicorn
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import Depends, FastAPI, Request
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

import helpers.monkey_patch  # do not remove, it is for TypeError: Object of type UUID is not JSON serializable
from api.v1.auth import router as auth_router
from api.v1.users import router as users_router
from core.logger import LOGGING
from core.settings import settings
from db import redis_db
from db.db import create_database
from helpers.auth import get_current_user_global
from helpers.exceptions import AuthException

tags_metadata = [
    {'name': 'users', 'description': 'Users in system'},
    {'name': 'auth', 'description': 'Login and such'},
]

app = FastAPI(
    title=settings.project_name,
    description=settings.project_description,
    version='1.0.0',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    openapi_tags=tags_metadata,
)


@app.on_event('startup')
async def startup():
    redis_db.redis = Redis(host=settings.redis.host, port=settings.redis.port, db=0, decode_responses=True)
    if settings.debug_mode:
        from models.user import User
        await create_database()


@app.on_event('shutdown')
async def shutdown():
    await redis_db.redis.close()

@AuthJWT.load_config
def get_config():
    return settings


@app.exception_handler(AuthJWTException)
@app.exception_handler(AuthException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException | AuthException):
    return ORJSONResponse(status_code=exc.status_code, content={'detail': exc.message})


@AuthJWT.token_in_denylist_loader
async def check_if_token_in_denylist(decrypted_token):
    jti = decrypted_token['jti']
    entry = await redis_db.redis.get(jti)
    return entry and entry == 'true'


app.include_router(
    users_router, prefix='/api/v1/users', tags=['users'], dependencies=[Depends(get_current_user_global)]
)
app.include_router(auth_router, prefix='/api/v1/auth', tags=['auth'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app', host='0.0.0.0', port=settings.app_port, log_config=LOGGING, log_level=logging.DEBUG, reload=True,
    )
