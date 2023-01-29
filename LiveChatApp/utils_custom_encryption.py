import json
import base64
import random
import string
from Crypto import Random
from Crypto.Cipher import AES

BLOCK_SIZE = 16


def pad(data_string):
    return data_string + (BLOCK_SIZE - len(data_string) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(data_string) % BLOCK_SIZE)


def unpad(data_string):
    return data_string[:-ord(data_string[len(data_string) - 1:])]


def aes256encrypt(raw, password, iv):
    raw = pad(raw)
    cipher = AES.new(password.encode('utf-8'), AES.MODE_CBC, iv)
    return base64.b64encode(cipher.encrypt(raw.encode('utf-8'))).decode("utf-8")


def aes256decrypt(enc, password, iv):
    enc = base64.b64decode(enc)
    cipher = AES.new(password.encode('utf-8'), AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc)).decode("utf-8")


def generate_random_key(length):
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))


class CustomEncrypt:

    def __init__(self):
        self.key = generate_random_key(16)
        self.iv = Random.new().read(AES.block_size)

    def encrypt(self, plain_text):
        encrypted_str = aes256encrypt(plain_text, self.key, self.iv)
        return ".".join([self.key, encrypted_str, base64.b64encode(self.iv).decode("utf-8")])

    def decrypt(self, encrypted_text):
        key, encrypted_text, iv = encrypted_text.split(".")
        iv = base64.b64decode(iv.encode("utf-8"))
        decrypted_text = aes256decrypt(encrypted_text.encode("utf-8"), key, iv)
        return decrypted_text
