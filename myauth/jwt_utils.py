import jwt

from datetime import datetime, UTC, timedelta
from django.conf import settings


SECRETE_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_jwt_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        'iat': datetime.now(UTC),
    }

    token = jwt.encode(payload, SECRETE_KEY, algorithm=ALGORITHM)
    return token

def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, SECRETE_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

