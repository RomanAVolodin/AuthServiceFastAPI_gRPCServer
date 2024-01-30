import http
import json
from enum import StrEnum, auto

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

User = get_user_model()


class Roles(StrEnum):
    ADMIN = auto()


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        url = settings.AUTH_API_LOCAL_LOGIN_URL
        payload = {'email': username, 'password': password}
        response = requests.post(url, data=json.dumps(payload))
        if response.status_code != http.HTTPStatus.OK:
            return None

        data = response.json()

        try:
            user, created = User.objects.get_or_create(
                id=data['id'],
            )
            user.email = data.get('email')
            user.first_name = data.get('first_name')
            user.last_name = data.get('last_name')
            user.is_admin = data.get('role') == Roles.ADMIN
            user.is_active = data.get('is_active')
            user.save()
        except Exception:
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
