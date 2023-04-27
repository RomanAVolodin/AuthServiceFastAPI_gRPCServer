from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_session
from helpers.exceptions import AuthException
from schemas.login_history import LoginHistoryCreateDto
from schemas.user import UserCreateDto, UserLoginDto, UserResponse
from services.auth import AuthService, get_auth_service
from services.login_history_repository import history_crud
from services.user_repository import users_crud

router = APIRouter()
router_refresh_token = APIRouter()


@router.post('/signup', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_dto: UserCreateDto, db: AsyncSession = Depends(get_session)) -> UserResponse:
    existed = await users_crud.get_by_email(db=db, email=user_dto.email)
    if existed:
        raise AuthException('User already exists', status_code=status.HTTP_409_CONFLICT)
    user = await users_crud.create(db=db, obj_in=user_dto)
    return user


@router.post('/login_inner', response_model=UserResponse)
async def login_inner(
    request: Request, user_dto: UserLoginDto, db: AsyncSession = Depends(get_session),
) -> UserResponse:
    user = await users_crud.get_by_email(db=db, email=user_dto.email)
    if not user:
        raise AuthException('Invalid credentials', status_code=status.HTTP_401_UNAUTHORIZED)
    if not user.check_password(user_dto.password):
        raise AuthException('Bad email or password', status_code=status.HTTP_401_UNAUTHORIZED)
    history = LoginHistoryCreateDto(
        user_id=user.id, user_agent=request.headers.get('User-Agent'), user_ip=request.client.host,
    )
    await history_crud.create(
        db=db, obj_in=history,
    )
    return user


@router.post('/login')
async def login(
    request: Request,
    user_dto: UserLoginDto,
    authorize: AuthJWT = Depends(),
    db: AsyncSession = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    user = await users_crud.get_by_email(db=db, email=user_dto.email)
    if not user:
        raise AuthException('Invalid credentials', status_code=status.HTTP_401_UNAUTHORIZED)

    if not user.check_password(user_dto.password):
        raise AuthException('Bad email or password', status_code=status.HTTP_401_UNAUTHORIZED)

    return await auth_service.generate_tokens(request=request, db=db, authorize=authorize, user=user)


@router.post('/refresh')
async def refresh(authorize: AuthJWT = Depends(), service: AuthService = Depends(get_auth_service)) -> dict[str, str]:
    await authorize.jwt_refresh_token_required()
    await service.revoke_both_tokens(authorize)
    current_user_id = await authorize.get_jwt_subject()
    access_token = await authorize.create_access_token(subject=current_user_id)
    access_jti = await authorize.get_jti(access_token)
    refresh_token = await authorize.create_refresh_token(
        subject=current_user_id, user_claims={'access_jti': access_jti}
    )
    return {'access_token': access_token, 'refresh_token': refresh_token}


@router.delete('/logout')
async def logout(authorize: AuthJWT = Depends(), service: AuthService = Depends(get_auth_service)) -> dict[str, str]:
    await authorize.jwt_refresh_token_required()
    await service.revoke_both_tokens(authorize)
    return {'detail': 'Access and refresh token has been revoke'}
