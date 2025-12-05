import os
import hashlib
import secrets

def generate_salt(length: int = 16) -> bytes:
    """Genera un salt aleatorio seguro."""
    return secrets.token_bytes(length)

def hash_password(password: str, salt: bytes) -> str:
    """Genera el hash seguro usando SHA-256."""
    pwd_salt = password.encode() + salt
    hash_value = hashlib.sha256(pwd_salt).digest()
    return hash_value.hex()
