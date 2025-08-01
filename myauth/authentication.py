import jwt

from django.conf import settings
from rest_framework import authentication, exceptions
from myauth.models import User

class JWTAuthentication(authentication.BaseAuthentication):
    """Кастомный класс аутентификации на основе JWT для Django REST Framework"""
    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).decode('utf-8')

        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Токен просрочен')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Неверный токен')

        user_id = payload.get('user_id')
        if not user_id:
            raise exceptions.AuthenticationFailed('Неверный токен: отсутствует user_id')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('Пользователь не найден')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('Пользователь неактивен')

        return user, token
