from typing import ClassVar as _ClassVar
from typing import Iterable as _Iterable
from typing import Mapping as _Mapping
from typing import Optional as _Optional
from typing import Union as _Union

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers

DESCRIPTOR: _descriptor.FileDescriptor

class GetAllUsersRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class GetMultipleUserRequest(_message.Message):
    __slots__ = ['ids']
    IDS_FIELD_NUMBER: _ClassVar[int]
    ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, ids: _Optional[_Iterable[str]] = ...) -> None: ...

class GetUserByTokenRequest(_message.Message):
    __slots__ = ['token']
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    def __init__(self, token: _Optional[str] = ...) -> None: ...

class GetUserRequest(_message.Message):
    __slots__ = ['id']
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class MultipleUserResponse(_message.Message):
    __slots__ = ['users']
    USERS_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[UserResponse]
    def __init__(self, users: _Optional[_Iterable[_Union[UserResponse, _Mapping]]] = ...) -> None: ...

class UserResponse(_message.Message):
    __slots__ = ['created_at', 'email', 'first_name', 'id', 'is_active', 'last_name', 'role']
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    created_at: str
    email: str
    first_name: str
    id: str
    is_active: bool
    last_name: str
    role: str
    def __init__(
        self,
        id: _Optional[str] = ...,
        email: _Optional[str] = ...,
        first_name: _Optional[str] = ...,
        last_name: _Optional[str] = ...,
        is_active: bool = ...,
        created_at: _Optional[str] = ...,
        role: _Optional[str] = ...,
    ) -> None: ...
