from abc import ABC, abstractmethod
import json
import os

from flask import Request
from werkzeug.exceptions import HTTPException

from helpers.auth_helpers import get_or_create_user_by_social_creds
from models import SocialNetworksEnum, User
from settings.extensions import fb, yandex, google


class SocialNetworkProvider(ABC):
    @abstractmethod
    def process_user(self, request: Request) -> User:
        pass


def get_provider(provider: str) -> SocialNetworkProvider:
    """
    'match --- case' still new and not obvious
    """
    provider = provider.lower()
    if provider == SocialNetworksEnum.Yandex.name.lower():
        return Yandex()
    if provider == SocialNetworksEnum.Google.name.lower():
        return Google()
    if provider == SocialNetworksEnum.Facebook.name.lower():
        return Facebook()
    raise HTTPException('Wrong credentials')


class Facebook(SocialNetworkProvider):
    def process_user(self, request: Request) -> User:
        code = request.json.get('code', None)
        fb.fetch_token(
            os.getenv('FACEBOOK_AUTH_TOKEN_URL'),
            client_secret=os.getenv('FACEBOOK_CLIENT_SECRET'),
            code=code,
        )
        r = fb.get(os.getenv('FACEBOOK_USERINFO_URL'))
        data = json.loads(r.content)
        return get_or_create_user_by_social_creds(
            social_id=data['id'],
            social_name=SocialNetworksEnum.Facebook,
            email=data.get('email'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            full_prov_data=data
        )


class Yandex(SocialNetworkProvider):
    def process_user(self, request: Request) -> User:
        code = request.json.get('code', None)
        yandex.fetch_token(
            os.getenv('YANDEX_AUTH_TOKEN_URL'),
            client_secret=os.getenv('YANDEX_CLIENT_SECRET'),
            code=code,
        )
        r = yandex.get(os.getenv('YANDEX_USERINFO_URL'))
        data = json.loads(r.content)
        return get_or_create_user_by_social_creds(
            social_id=data['id'],
            social_name=SocialNetworksEnum.Yandex,
            email=data.get('default_email'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            full_prov_data=data
        )


class Google(SocialNetworkProvider):
    def process_user(self, request: Request) -> User:
        code = request.json.get('code', None)
        google.fetch_token(
            os.getenv('GOOGLE_AUTH_TOKEN_URL'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
            code=code,
        )
        r = google.get(os.getenv('GOOGLE_USERINFO_URL'))
        data = json.loads(r.content)
        return get_or_create_user_by_social_creds(
            social_id=data['id'],
            social_name=SocialNetworksEnum.Google,
            email=data.get('email'),
            first_name=data.get('given_name'),
            last_name=data.get('family_name'),
            full_prov_data=data
        )
