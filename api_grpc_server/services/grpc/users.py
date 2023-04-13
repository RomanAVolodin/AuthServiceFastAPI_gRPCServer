import time

import grpc
import jwt

from core.grpc import users_pb2, users_pb2_grpc
from core.settings import settings
from db.db import async_session
from schemas.user import UserInDb
from services.user_repository import users_crud


def decode_token(token: str) -> dict | None:
    try:
        decoded_token = jwt.decode(token, settings.authjwt_secret_key, algorithms=[settings.authjwt_algorithm])
        return decoded_token if decoded_token['exp'] >= time.time() else None
    except Exception:
        return None


class UsersFetcher(users_pb2_grpc.DetailerServicer):
    async def DetailsByToken(
        self, request: users_pb2.GetUserByTokenRequest, context: grpc.aio.ServicerContext,
    ) -> users_pb2.UserResponse:
        user_id = decode_token(request.token).get('sub')
        if not user_id:
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details('Token is not valid')
            return users_pb2.UserResponse()

        async with async_session() as session:
            item = await users_crud.get(db=session, id=user_id)
            user = UserInDb.from_orm(item)
            return self.__generate_user_response(user)

    async def DetailsById(
        self, request: users_pb2.GetUserRequest, context: grpc.aio.ServicerContext,
    ) -> users_pb2.UserResponse:
        async with async_session() as session:
            item = await users_crud.get(db=session, id=request.id)
            user = UserInDb.from_orm(item)
            return self.__generate_user_response(user)

    async def MultipleDetailsByIds(
        self, request: users_pb2.GetMultipleUserRequest, context: grpc.aio.ServicerContext,
    ) -> users_pb2.MultipleUserResponse:
        async with async_session() as session:
            items = await users_crud.get_all_by_ids(db=session, ids=request.ids)
            users = [UserInDb.from_orm(user) for user in items]
        users_response = self.__prepare_users_response(users)
        return users_pb2.MultipleUserResponse(users=users_response)

    async def GetAllUsers(
        self, request: users_pb2.GetAllUsersRequest, context: grpc.aio.ServicerContext,
    ) -> users_pb2.MultipleUserResponse:
        async with async_session() as session:
            items = await users_crud.get_multi(db=session)
            users = [UserInDb.from_orm(user) for user in items]
        users_response = self.__prepare_users_response(users)
        return users_pb2.MultipleUserResponse(users=users_response)

    def __generate_user_response(self, user: UserInDb) -> users_pb2.UserResponse:
        return users_pb2.UserResponse(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            created_at=str(user.created_at),
            role=str(user.role),
        )

    def __prepare_users_response(self, users: list[UserInDb]) -> list[users_pb2.UserResponse]:
        users_response = []
        for user in users:
            users_response.append(self.__generate_user_response(user))
        return users_response
