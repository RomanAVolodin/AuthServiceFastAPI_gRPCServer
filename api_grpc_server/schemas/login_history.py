from uuid import UUID

from pydantic import BaseModel


class LoginHistoryCreateDto(BaseModel):
    user_agent: str | None
    user_ip: str
    user_id: UUID
    access_token: UUID | None
    refresh_token: UUID | None


class LoginHistoryResponse(BaseModel):
    user_agent: str | None
    user_ip: str
    user_id: UUID
    access_token: UUID | None
    refresh_token: UUID | None

    class Config:
        orm_mode = True
        use_enum_values = True
