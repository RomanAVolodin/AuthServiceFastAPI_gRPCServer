import logging
import os

import uvicorn
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from async_oauthlib import OAuth2Session
from fastapi import Depends, FastAPI, Request, status, HTTPException
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from redis.asyncio import Redis
from starlette.middleware.cors import CORSMiddleware

import helpers.monkey_patch  # do not remove, it is for TypeError: Object of type UUID is not JSON serializable
from api.v1.auth import router as auth_router
from api.v1.socials import router as socials_router
from api.v1.users import router as users_router
from core import extensions
from core.logger import LOGGING
from core.settings import settings
from db import redis_db
from db.db import create_database
from helpers.auth import get_current_user_global
from helpers.exceptions import AuthException
from helpers.tracer import configure_tracer

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


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
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)

app.mount('/static', StaticFiles(directory='static'), name='static')

app.add_middleware(
    CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'],
)


@app.middleware('http')
async def before_request(request: Request, call_next):
    response = await call_next(request)
    if settings.request_id_needed:
        request_id = request.headers.get('X-Request-Id')
        if not request_id:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST, content={'detail': 'X-Request-Id is required'}
            )
    return response


@app.on_event('startup')
async def startup():
    redis_db.redis = Redis(host=settings.redis.host, port=settings.redis.port, db=0, decode_responses=True)
    await FastAPILimiter.init(redis_db.redis)

    extensions.google = OAuth2Session(
        settings.google_client_id,
        redirect_uri=settings.social_auth_redirect_url,
        scope='https://www.googleapis.com/auth/userinfo.email openid https://www.googleapis.com/auth/userinfo.profile',
    )
    extensions.yandex = OAuth2Session(settings.yandex_client_id, redirect_uri=settings.social_auth_redirect_url,)

    if settings.debug_mode:
        from models.user import User

        await create_database()


@app.on_event('shutdown')
async def shutdown():
    await redis_db.redis.close()
    await extensions.google.close()
    await extensions.yandex.close()


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


@app.get('/')
async def root():
    return {'message': 'Hello World'}


app.include_router(
    users_router, prefix='/api/v1/users', tags=['users'], dependencies=[Depends(get_current_user_global)],
)
app.include_router(auth_router, prefix='/api/v1/auth', tags=['auth'])
app.include_router(socials_router, prefix='/api/v1/socials', tags=['socials'])

if settings.enable_tracer:
    configure_tracer()
    FastAPIInstrumentor.instrument_app(app)


if __name__ == '__main__':
    uvicorn.run(
        'main:app', host='0.0.0.0', port=settings.app_port, log_config=LOGGING, log_level=logging.DEBUG, reload=True,
    )
