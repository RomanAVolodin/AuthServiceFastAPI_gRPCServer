from fastapi import Request

from schemas.user import UserInDb


class AuthRequest(Request):
    custom_user: UserInDb
