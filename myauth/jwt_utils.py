import jwt

from datetime import timedelta
from django.utils import timezone
from django.conf import settings

from myauth.models import RefreshToken, BlacklistedToken

SECRETE_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAY = 7

def create_jwt_token(user_id):
    """Создает JWT-токен с заданным идентификатором пользователя и временем жизни"""
    payload = {
        'user_id': user_id,
        'exp': timezone.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        'iat': timezone.now(),
    }

    token = jwt.encode(payload, SECRETE_KEY, algorithm=ALGORITHM)
    return token

def create_jwt_tokens(user_id):
    """Создает JWT-токены (access_token и refresh_token) с заданным идентификатором пользователя
     и временем жизни"""
    access_payload = {
        'user_id': user_id,
        'type': 'access',
        'exp': timezone.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        'iat': timezone.now(),
    }
    access_token = jwt.encode(access_payload, SECRETE_KEY, algorithm=ALGORITHM)

    refresh_payload = {
        'user_id': user_id,
        'type': 'refresh',
        'exp': timezone.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAY),
        'iat': timezone.now()
    }
    refresh_token = jwt.encode(refresh_payload, SECRETE_KEY, algorithm=ALGORITHM)

    RefreshToken.objects.create(
        user_id=user_id,
        token=refresh_token,
        expired_at=timezone.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAY)
    )

    return {'access_token': access_token, 'refresh_token': refresh_token}

def decode_jwt_token(token):
    """Декодирует JWT-токен и возвращает полезную нагрузку, если токен валиден и не истёк"""
    try:
        payload = jwt.decode(token, SECRETE_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def is_token_blacklisted(token):
    """Проверяет есть ли токен в Blacklisted"""
    try:
        blacklisted = BlacklistedToken.objects.get(token=token)
        if blacklisted.is_expired():
            blacklisted.delete()
            return False
        return True
    except BlacklistedToken.DoesNotExist:
        return False


def clean_user_tokens(user_id):
    """проверка и удаление из БД истекших RefreshToken и BlacklistedToken"""
    now = timezone.now()
    RefreshToken.objects.filter(user_id=user_id, expired_at__lt=now).delete()

    BlacklistedToken.objects.filter(user_id=user_id, expired_at__lt=now).delete()

