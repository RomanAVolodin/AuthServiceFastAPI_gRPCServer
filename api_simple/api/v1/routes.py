from typing import Annotated
from uuid import UUID

import grpc
from core.auth import security_jwt_local
from core.grpc import users_pb2, users_pb2_grpc
from core.settings import settings
from fastapi import APIRouter, Body, Depends
from google.protobuf.json_format import MessageToDict

router = APIRouter()


@router.get('/user/{user_id}')
async def get_user(user_id: UUID):
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = users_pb2_grpc.DetailerStub(channel)
        request = users_pb2.GetUserRequest(id=str(user_id))
        response: users_pb2.UserResponse = await stub.DetailsById(request)
    return {'users': MessageToDict(response)}


@router.get(
    '/users',
    description="""Принимает список id для похода в gRPC за пользователями.\r\n Пример: [
    "a184c3b4-1038-418c-bd50-4405bb813154",
    "bc85cf72-c892-4083-ade4-9b371c1c39eb"]""",
)
async def get_users_by_ids(
    ids: Annotated[
        list[UUID],
        Body(
            example=[
                'a184c3b4-1038-418c-bd50-4405bb813154',
                'bc85cf72-c892-4083-ade4-9b371c1c39eb',
            ]
        ),
    ],
    user: Annotated[dict, Depends(security_jwt_local)],
):
    async with grpc.aio.insecure_channel(f'{settings.grpc_host}:{settings.grpc_port}') as channel:
        stub = users_pb2_grpc.DetailerStub(channel)
        request = users_pb2.GetMultipleUserRequest(ids=[str(user_id) for user_id in ids])
        response: users_pb2.UserResponse = await stub.MultipleDetailsByIds(request)
    return MessageToDict(response)


@router.get(
    '/all-users',
    description='Список всех пользователей',
)
async def all_users():
    async with grpc.aio.insecure_channel(f'{settings.grpc_host}:{settings.grpc_port}') as channel:
        stub = users_pb2_grpc.DetailerStub(channel)
        request = users_pb2.GetAllUsersRequest()
        response: users_pb2.UserResponse = await stub.GetAllUsers(request)
    return MessageToDict(response)
