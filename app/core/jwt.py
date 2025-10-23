import time, jwt
from app.core.config import settings

def create_token(sub: str, role: str, minutes: int):
    now = int(time.time())
    payload = {"sub": sub, "role": role, "iat": now, "exp": now + minutes*60}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)

def decode_token(token: str):
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])
