from uuid import UUID

from pydantic import BaseModel


class LoginHistoryCreateDto(BaseModel):
    user_agent: str | None
    user_ip: str
    user_id: UUID
    access_token: UUID
    refresh_token: UUID


class LoginHistoryResponse(BaseModel):
    user_agent: str | None
    user_ip: str
    user_id: UUID
    access_token: UUID
    refresh_token: UUID

    class Config:
        orm_mode = True
        use_enum_values = True
