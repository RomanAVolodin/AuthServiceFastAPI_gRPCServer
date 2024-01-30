import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.settings import settings
from db.db import get_session
from helpers.auth import roles_required
from helpers.auth_request import AuthRequest
from models.user import UserRole
from schemas.login_history import LoginHistoryResponse
from schemas.user import UserInDb, UserResponse, UserShort, UserUpdateRoleDto
from services.login_history_repository import history_crud
from services.user_repository import users_crud

router = APIRouter()


@router.get('/', response_model=list[UserShort])
@roles_required(roles_list=[UserRole.admin, UserRole.privileged_user])
async def read_users(
    *,
    request: AuthRequest,
    db: AsyncSession = Depends(get_session),
    skip: int = Query(0, description='Items to skip', ge=0),
    limit: int = Query(settings.pagination_limit, description='Items amount on page', ge=1),
) -> list[UserShort]:
    entities = await users_crud.get_multi(db=db, skip=skip, limit=limit)
    return entities


@router.get('/details/{user_id}', response_model=UserResponse)
@roles_required(roles_list=[UserRole.admin, UserRole.privileged_user])
async def read_user(
    *,
    request: AuthRequest,
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
) -> UserResponse:
    entity = await users_crud.get(db=db, id=user_id)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return entity


@router.post('/update-role', response_model=UserResponse)
@roles_required(roles_list=[UserRole.admin])
async def read_user(
    *,
    request: AuthRequest,
    dto: UserUpdateRoleDto,
    db: AsyncSession = Depends(get_session),
) -> UserResponse:
    entity = await users_crud.set_role_for_user(db=db, user_id=dto.user_id, role=dto.role)
    return entity


@router.get('/me', response_model=UserResponse)
async def get_user(request: AuthRequest) -> UserInDb:
    return request.custom_user


@router.get('/history', response_model=list[LoginHistoryResponse])
async def get_history(
    request: AuthRequest,
    db: AsyncSession = Depends(get_session),
    skip: int = Query(0, description='Items to skip', ge=0),
    limit: int = Query(settings.pagination_limit, description='Items amount on page', ge=1),
) -> list[LoginHistoryResponse]:
    return await history_crud.get_all_for_user(request.custom_user.id, db=db, skip=skip, limit=limit)
