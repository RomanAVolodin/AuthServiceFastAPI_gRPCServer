from api.v1.routes import router

import uvicorn
from fastapi import FastAPI, Depends

from core.auth import security_jwt_local, security_jwt_remote

app = FastAPI()


@app.get('/')
async def root():
    return {'message': 'Hello World'}


app.include_router(
    router,
    prefix='/api/v1',
    tags=['Пользователи из сервиса авторизации по gRPC (авторизация декодированием токена в этом же сервисе)'],
    dependencies=[Depends(security_jwt_local)],
)

app.include_router(
    router,
    prefix='/api/v1/remote_auth',
    tags=['Пользователи из сервиса авторизации по gRPC (авторизация походом в сервис авторизации по gRPC)'],
    dependencies=[Depends(security_jwt_remote)],
)


if __name__ == '__main__':
    uvicorn.run(
        'main:app', host='0.0.0.0', port=8085, reload=True,
    )
