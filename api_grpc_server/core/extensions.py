from async_oauthlib import OAuth2Session

from models.user import SocialNetworksEnum

google: OAuth2Session | None = None
yandex: OAuth2Session | None = None


async def get_providers() -> dict[SocialNetworksEnum, OAuth2Session]:
    return {
        SocialNetworksEnum.Google: google,
        SocialNetworksEnum.Yandex: yandex,
    }
