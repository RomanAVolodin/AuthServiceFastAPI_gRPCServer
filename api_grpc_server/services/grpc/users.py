import grpc

from core.grpc import users_pb2, users_pb2_grpc
from db.db import async_session
from schemas.user import UserInDb
from services.user_repository import users_crud


class UsersFetcher(users_pb2_grpc.DetailerServicer):
    async def DetailsById(
        self, request: users_pb2.GetUserRequest, context: grpc.aio.ServicerContext,
    ) -> users_pb2.UserResponse:
        async with async_session() as session:
            item = await users_crud.get(db=session, id=request.id)
            user = UserInDb.from_orm(item)
            return users_pb2.UserResponse(
                id=str(user.id),
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                is_active=user.is_active,
                created_at=str(user.created_at),
                role=str(user.role),
            )

    async def MultipleDetailsByIds(
        self, request: users_pb2.GetMultipleUserRequest, context: grpc.aio.ServicerContext,
    ) -> users_pb2.MultipleUserResponse:
        users_response = []
        async with async_session() as session:
            items = await users_crud.get_all_by_ids(db=session, ids=request.ids)
            users = [UserInDb.from_orm(user) for user in items]

        for user in users:
            users_response.append(
                users_pb2.UserResponse(
                    id=str(user.id),
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    is_active=user.is_active,
                    created_at=str(user.created_at),
                    role=str(user.role),
                )
            )

        return users_pb2.MultipleUserResponse(users=users_response)

    async def GetAllUsers(
        self, request: users_pb2.GetAllUsersRequest, context: grpc.aio.ServicerContext,
    ) -> users_pb2.MultipleUserResponse:
        users_response = []
        async with async_session() as session:
            items = await users_crud.get_multi(db=session)
            users = [UserInDb.from_orm(user) for user in items]

        for user in users:
            users_response.append(
                users_pb2.UserResponse(
                    id=str(user.id),
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    is_active=user.is_active,
                    created_at=str(user.created_at),
                    role=str(user.role),
                )
            )

        return users_pb2.MultipleUserResponse(users=users_response)
