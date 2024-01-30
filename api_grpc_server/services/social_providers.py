from abc import ABC, abstractmethod

import httpx as httpx
from async_oauthlib import OAuth2Session
from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.settings import settings
from models.user import SocialNetworksEnum, User
from services.socials_repository import socials_crud


class SocialNetworkProvider(ABC):
    @abstractmethod
    async def process_user(self, db: AsyncSession, code: str, provider: OAuth2Session) -> User:
        ...

    async def fetch_data(
        self, code: str, provider: OAuth2Session, auth_token_url: str, userinfo_url: str, client_secret: str
    ):
        token = await provider.fetch_token(
            auth_token_url,
            client_secret=client_secret,
            code=code,
        )
        async with httpx.AsyncClient() as client:
            headers = {
                'Authorization': f'OAuth {token["access_token"]}',
            }
            r = await client.get(userinfo_url, headers=headers)
        data = r.json()
        return data


def get_provider(provider: SocialNetworksEnum) -> SocialNetworkProvider:
    """
    'match --- case' still new and not obvious
    """
    if provider == SocialNetworksEnum.Yandex:
        return Yandex()
    if provider == SocialNetworksEnum.Google:
        return Google()
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Wrong credentials')


class Yandex(SocialNetworkProvider):
    async def process_user(self, db: AsyncSession, code: str, provider: OAuth2Session) -> User:
        data = await self.fetch_data(
            code,
            provider,
            settings.yandex_auth_token_url,
            settings.yandex_userinfo_url,
            settings.yandex_client_secret,
        )
        return await socials_crud.get_or_create_user_by_social_creds(
            db,
            social_id=data['id'],
            social_name=SocialNetworksEnum.Yandex,
            email=data.get('default_email'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            full_prov_data=data,
        )


class Google(SocialNetworkProvider):
    async def process_user(self, db: AsyncSession, code: str, provider: OAuth2Session) -> User:
        data = await self.fetch_data(
            code,
            provider,
            settings.google_auth_token_url,
            settings.google_userinfo_url,
            settings.google_client_secret,
        )
        return await socials_crud.get_or_create_user_by_social_creds(
            db,
            social_id=data['id'],
            social_name=SocialNetworksEnum.Google,
            email=data.get('email'),
            first_name=data.get('given_name'),
            last_name=data.get('family_name'),
            full_prov_data=data,
        )
