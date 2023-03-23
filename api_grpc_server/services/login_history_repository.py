from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.user import LoginHistory
from schemas.login_history import LoginHistoryCreateDto

from .base import RepositoryDB


class LoginHistoryRepository(RepositoryDB[LoginHistory, LoginHistoryCreateDto, LoginHistoryCreateDto]):
    async def get_all_for_user(self, user_id: UUID, db: AsyncSession, *, skip=0, limit=10) -> list[LoginHistory]:
        statement = select(self._model).where(self._model.user_id == user_id).offset(skip).limit(limit)
        results = await db.execute(statement=statement)
        return results.scalars().all()


history_crud = LoginHistoryRepository(LoginHistory)
