import enum
import uuid
from datetime import datetime

from passlib.context import CryptContext
from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, ForeignKey, Index, String, Text, text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship

from db.db import Base

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


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
        self.password = pwd_context.hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.is_active = True

    def check_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password)

    def __repr__(self) -> str:
        return f'<id {self.id}>'


def create_partition(target, connection, **kw) -> None:
    """creating partition by user_sign_in"""
    connection.execute(
        text(
            """CREATE TABLE IF NOT EXISTS "logins_history_smart" PARTITION OF "logins_history" FOR VALUES IN ('smart')"""
        )
    )
    connection.execute(
        text(
            """CREATE TABLE IF NOT EXISTS "logins_history_mobile" PARTITION OF "logins_history" FOR VALUES IN ('mobile')"""
        )
    )
    connection.execute(
        text("""CREATE TABLE IF NOT EXISTS "logins_history_web" PARTITION OF "logins_history" FOR VALUES IN ('web')""")
    )


class LoginHistory(Base):
    __tablename__ = 'logins_history'
    __table_args__ = (
        UniqueConstraint('id', 'user_device_type'),
        {
            'postgresql_partition_by': 'LIST (user_device_type)',
            'listeners': [('after_create', create_partition)],
        },
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(DateTime, default=datetime.utcnow)
    user_agent = Column(String(), nullable=False)
    user_ip = Column(String(100), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    access_token = Column(UUID(as_uuid=True), nullable=True)
    refresh_token = Column(UUID(as_uuid=True), nullable=True)
    user_device_type = Column(Text, primary_key=True)

    user = relationship('User', uselist=False, back_populates='history')

    def __init__(
        self, user_id: UUID, user_agent: str, user_ip: str, access_token: str, refresh_token: str, user_device_type: str
    ) -> None:
        self.user_id = user_id
        self.user_agent = user_agent
        self.user_ip = user_ip
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.user_device_type = user_device_type

    def __repr__(self) -> str:
        return f'<id {self.id}>'


class SocialNetworksEnum(enum.Enum):
    Yandex = 'Yandex'
    Google = 'Google'


class SocialAccount(Base):
    __tablename__ = 'social_accounts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    user = relationship(
        User,
        backref=backref('social_accounts', cascade='all,delete', lazy=True),
    )

    social_id = Column(Text, nullable=False)
    social_name = Column(Enum(SocialNetworksEnum))
    full_prov_data = Column(JSON, nullable=True)

    __table_args__ = (UniqueConstraint('social_id', 'social_name', name='social_pk'),)

    def __init__(
        self, user_id: UUID, social_id: str, social_name: SocialNetworksEnum, full_prov_data: str | None = None
    ) -> None:
        self.user_id = user_id
        self.social_id = social_id
        self.social_name = social_name
        self.full_prov_data = full_prov_data

    def __repr__(self):
        return f'<SocialAccount {self.social_name}:{self.user_id}>'
