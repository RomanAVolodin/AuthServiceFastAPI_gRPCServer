import http
import time

import grpc
from jose import jwt
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.grpc import users_pb2_grpc, users_pb2
from core.settings import settings


def decode_token(token: str) -> dict | None:
    try:
        decoded_token = jwt.decode(token, settings.authjwt_secret_key, algorithms=[settings.authjwt_algorithm])
        return decoded_token if decoded_token['exp'] >= time.time() else None
    except Exception:
        return None


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if not credentials.scheme == 'Bearer':
                raise HTTPException(status_code=http.HTTPStatus.UNAUTHORIZED, detail='Invalid authentication scheme.')
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN, detail='Invalid token or expired token.')
            return credentials.credentials
        raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN, detail='Invalid authorization code.')

    @staticmethod
    def verify_jwt(jwt_token: str) -> bool:
        return decode_token(jwt_token) is not None


security_jwt_local = JWTBearer()


class JWTBearerRemoteGrpc(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if not credentials.scheme == 'Bearer':
                raise HTTPException(status_code=http.HTTPStatus.UNAUTHORIZED, detail='Invalid authentication scheme.')
            if not await self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN, detail='Invalid token or expired token.')
            return credentials.credentials
        raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN, detail='Invalid authorization code.')

    @staticmethod
    async def verify_jwt(jwt_token: str) -> bool:
        async with grpc.aio.insecure_channel(f'{settings.grpc_host}:{settings.grpc_port}') as channel:
            stub = users_pb2_grpc.DetailerStub(channel)
            request = users_pb2.GetUserByTokenRequest(token=jwt_token)
            try:
                response: users_pb2.UserResponse = await stub.DetailsByToken(request)
                if response is not None:
                    return True
            except grpc.RpcError as e:
                raise HTTPException(status_code=http.HTTPStatus.UNAUTHORIZED, detail=e.details())
        return False


security_jwt_remote = JWTBearerRemoteGrpc()
