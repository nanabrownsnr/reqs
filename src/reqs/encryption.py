from cryptography.fernet import Fernet

from reqs.config import settings


cipher = Fernet(settings.encryption_key)


def encrypt_data(data: bytes) -> bytes:
    return cipher.encrypt(data)


def decrypt_data(data: bytes) -> bytes:
    return cipher.decrypt(data)
