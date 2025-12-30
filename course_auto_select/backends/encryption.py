"""Encryption helpers for portal login."""

import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


class LoginEncryptModel:
    """Mirrors the client-side AES password obfuscation used by CAS."""

    _AES_CHARS = "ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678"

    def __init__(self, salt: str = "") -> None:
        self.salt = salt

    def random_string(self, length: int) -> str:
        return "".join(random.choice(self._AES_CHARS) for _ in range(length))

    def get_aes_string(self, plain: str, key_str: str, iv_str: str) -> str:
        key_bytes = key_str.strip().encode("utf-8")
        iv_bytes = iv_str.encode("utf-8")
        if len(key_bytes) != 16:
            key_bytes = key_bytes[:16] if len(key_bytes) > 16 else key_bytes.ljust(16, b"\0")
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
        encrypted_bytes = cipher.encrypt(pad(plain.encode("utf-8"), AES.block_size))
        return __import__("base64").b64encode(encrypted_bytes).decode("utf-8")

    def encrypt_aes(self, plain: str, salt: str) -> str:
        if not salt:
            return plain
        new_plain = self.random_string(64) + plain
        iv = self.random_string(16)
        return self.get_aes_string(new_plain, salt, iv)

    def set_salt(self, salt: str) -> None:
        self.salt = salt

    def encrypt_password(self, password: str) -> str:
        try:
            return self.encrypt_aes(password, self.salt)
        except Exception:
            return password
