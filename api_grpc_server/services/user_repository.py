from uuid import UUID

from fastapi import status
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from helpers.exceptions import AuthException
from models.user import User as UserModel
from models.user import UserRole
from schemas.user import UserCreateDto, UserUpdateDto

from .base import RepositoryDB


class UsersRepository(RepositoryDB[UserModel, UserCreateDto, UserUpdateDto]):
    async def get_by_email(self, db: AsyncSession, email: EmailStr) -> UserModel | None:
        statement = select(UserModel).where(UserModel.email == email)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def set_role_for_user(self, db: AsyncSession, user_id: UUID, role: UserRole) -> UserModel | None:
        statement = select(UserModel).where(UserModel.id == user_id)
        results = await db.execute(statement=statement)
        user = results.scalar_one_or_none()
        if not user:
            raise AuthException(message='User not found', status_code=status.HTTP_404_NOT_FOUND)

        user.role = role
        await db.commit()
        await db.refresh(user)
        return user

    async def get_all_by_ids(self, db: AsyncSession, *, ids=list[str]) -> list[UserModel]:
        statement = select(UserModel).where(UserModel.id.in_(ids))
        results = await db.execute(statement=statement)
        return results.scalars().all()

    async def create_admin(self, db: AsyncSession, *, dto: UserCreateDto) -> UserModel:
        obj_in_data = jsonable_encoder(dto)
        admin = UserModel(**obj_in_data)
        admin.role = UserRole.admin
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        return admin


users_crud = UsersRepository(UserModel)
