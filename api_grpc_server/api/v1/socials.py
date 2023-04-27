from typing import Annotated

from async_fastapi_jwt_auth import AuthJWT
from async_oauthlib import OAuth2Session
from fastapi import APIRouter, Depends, Path, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from core.extensions import get_providers
from core.settings import settings
from db.db import get_session
from models.user import SocialNetworksEnum
from services.auth import AuthService, get_auth_service
from services.social_providers import get_provider

router = APIRouter()


templates = Jinja2Templates(directory='templates')


@router.get('/', response_class=HTMLResponse)
def main_page(
    request: Request,
    code: str | None = Query(None, description='Code from auth provider'),
    providers: dict[SocialNetworksEnum, OAuth2Session] = Depends(get_providers),
):
    google_authorization_url, state = providers[SocialNetworksEnum.Google].authorization_url(
        settings.google_auth_base_url
    )
    yandex_authorization_url, state = providers[SocialNetworksEnum.Yandex].authorization_url(
        settings.yandex_auth_base_url
    )
    return templates.TemplateResponse(
        'index.html',
        {
            'request': request,
            'google_authorization_url': google_authorization_url,
            'yandex_authorization_url': yandex_authorization_url,
            'code': code,
        },
    )


@router.post('/login/{provider_name}')
async def login_by_social_network(
    request: Request,
    provider_name: Annotated[SocialNetworksEnum, Path(description='Auth provider name')],
    code: Annotated[str, Query(description='Code from auth provider')],
    authorize: AuthJWT = Depends(),
    db: AsyncSession = Depends(get_session),
    providers: dict[SocialNetworksEnum, OAuth2Session] = Depends(get_providers),
    auth_service: AuthService = Depends(get_auth_service),
):
    provider = get_provider(provider_name)
    user = await provider.process_user(db, code, providers[provider_name])

    return await auth_service.generate_tokens(request=request, db=db, authorize=authorize, user=user)
