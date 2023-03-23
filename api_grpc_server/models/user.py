import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from db.db import Base


class UserRole(enum.Enum):
    user = 'user'
    privileged_user = 'privileged_user'
    admin = 'admin'

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    is_active = Column(Boolean(True))
    created_at = Column(DateTime, default=datetime.utcnow)
    role = Column(Enum(UserRole, name='user_roles'), default=UserRole.user, nullable=False)
    history = relationship('LoginHistory', uselist=True, back_populates='user', passive_deletes=True)

    Index('idx_user_email_password', 'email', 'password')

    def __init__(self, email: str, password: str, first_name: str, last_name: str) -> None:
        self.email = email
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.is_active = True

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f'<id {self.id}>'


class LoginHistory(Base):
    __tablename__ = 'logins_history'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(DateTime, default=datetime.utcnow)
    user_agent = Column(String(), nullable=False)
    user_ip = Column(String(100), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    access_token = Column(UUID(as_uuid=True), nullable=True)
    refresh_token = Column(UUID(as_uuid=True), nullable=True)

    user = relationship('User', uselist=False, back_populates='history')

    def __init__(self, user_id: UUID, user_agent: str, user_ip: str, access_token: str, refresh_token: str) -> None:
        self.user_id = user_id
        self.user_agent = user_agent
        self.user_ip = user_ip
        self.access_token = access_token
        self.refresh_token = refresh_token

    def __repr__(self) -> str:
        return f'<id {self.id}>'
