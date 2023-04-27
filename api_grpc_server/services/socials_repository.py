import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from models.user import SocialAccount as SocialAccountModel
from models.user import SocialNetworksEnum
from models.user import User as UserModel
from schemas.user import SocialCreateDto, SocialUpdateDto, UserCreateDto

from .base import RepositoryDB
from .user_repository import users_crud


class SocialsRepository(RepositoryDB[SocialAccountModel, SocialCreateDto, SocialUpdateDto]):
    async def get_by_name_and_id(
        self, db: AsyncSession, name: SocialNetworksEnum, id: str
    ) -> SocialAccountModel | None:
        statement = (
            select(SocialAccountModel)
            .where(SocialAccountModel.social_name == name)
            .where(SocialAccountModel.social_id == id)
            .options(joinedload(SocialAccountModel.user))
        )
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_or_create_user_by_social_creds(
        self,
        db: AsyncSession,
        social_id: str,
        social_name: SocialNetworksEnum,
        email: str | None,
        last_name: str | None,
        first_name: str | None,
        full_prov_data: str | None = None,
    ) -> UserModel:
        social_account = await self.get_by_name_and_id(db, social_name, social_id)
        if social_account:
            return social_account.user
        auto_email = f'auto_{social_id}@{social_name.name}.ru' if not email else email
        auto_password = uuid.uuid4().hex.upper()[0:6]
        user = await users_crud.create(
            db,
            obj_in=UserCreateDto(email=auto_email, password=auto_password, last_name=last_name, first_name=first_name),
        )
        _ = await self.create(
            db,
            obj_in=SocialCreateDto(
                user_id=user.id, social_id=social_id, social_name=social_name, full_prov_data=str(full_prov_data)
            ),
        )
        return user


socials_crud = SocialsRepository(SocialAccountModel)
