import hmac
import sys
import hashlib
import random
import string
import logging

from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Cipher import PKCS1_v1_5 as CipherPKCS1_v1_5
from Crypto.Signature import PKCS1_v1_5 as SignaturePKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode
from pkcs7 import PKCS7Encoder

logger = logging.getLogger(__name__)

"""
function: new_keys
input params:
    keysize: length of the key which to be generated
output params:
    public: public key
    private: private key

returns private & public key pair
"""


def new_keys(keysize):
    random_generator = Random.new().read
    key = RSA.generate(keysize, random_generator)
    private, public = key, key.publickey()
    file_key = open('files/private/allincall_private_key.pem', 'w')
    file_key.write(private.exportKey('PEM'))
    file_key = open('files/private/allincall_public_key.pem', 'w')
    file_key.write(public.exportKey('PEM'))
    return public, private


"""
function: import_key
input params:
    externKey: key has to be imported
output params:
    returns imported RSA key
"""


def import_key(extern_key):
    return RSA.import_key(extern_key)


"""
function: b64encoding
input params:
    str: string which is to encoded using base 64
output params:

returns base64 encoded string
"""


def b64encoding(str):
    return b64encode(str)


"""
function: b64decoding
input params:
    str: string which is to decoded using base 64
output params:

returns decoded string
"""


def b64decoding(str):
    return b64decode(str)


"""
function: rsa_encrypt_pkcs1_v1_5
input params:
    plain_text: text which has to be encrypted
    public_key: public key
output params:
    returns encrypted message
"""


def rsa_encrypt_pkcs1_v1_5(plain_text, public_key):
    cipher = CipherPKCS1_v1_5.new(public_key)
    ciphertext = cipher.encrypt(plain_text)
    return b64encoding(ciphertext)


"""
function: rsa_decrypt_pkcs1_v1_5
input params:
    encrypted_message: encrypted message
    private_key: private key
output params:
    returns decrypted message
"""


def rsa_decrypt_pkcs1_v1_5(encrypted_message, private_key):
    encrypted_message = b64decoding(encrypted_message)
    cipher = CipherPKCS1_v1_5.new(private_key)
    message = cipher.decrypt(encrypted_message, "Error while descryption")
    return message


"""
function: rsa_encrypt
input params:
    plain_text: text which has to be encrypted
    public_key: public key
output params:
    returns encrypted message
"""


def rsa_encrypt(plain_text, public_key):
    public_key = RSA.importKey(open(public_key, 'r').read())
    cipher = PKCS1_OAEP.new(public_key)
    cipher_text = cipher.encrypt(plain_text.encode('utf-8'))
    cipher_text = b64encode(cipher_text)
    return cipher_text


"""
function: rsa_decrypt
input params:
    encrypted_message: encrypted message
    private_key: private key
output params:
    returns decrypted message
"""


def rsa_decrypt(encrypted_message, private_key):
    private_key = RSA.importKey(open(private_key, 'r').read())
    encrypted_message = b64decode(encrypted_message)
    cipher = PKCS1_OAEP.new(private_key)
    plain_text = cipher.decrypt(encrypted_message)
    return plain_text


"""
function: aes_cbc_encrypt
input params:
    plain_text: text which has to be encrypted
    passphrase: passphrase is the key which can be 128, 192, or 256 bits (16, 24, or 32 bytes)
    IV: IV is used to mix up the output of a encryption when input is same, 
    so the IV is chosen as a random string, and use it as part of the encryption output, 
    and then use it to decrypt the message.
output params:
    returns encrypted message
"""


def aes_cbc_encrypt(plain_text, passphrase, iv):
    encoder = PKCS7Encoder()
    plain_text = encoder.encode(plain_text)
    aes = AES.new(passphrase, AES.MODE_CBC, iv)
    encrypted_message = aes.encrypt(plain_text)
    encrypted_message = b64encoding(encrypted_message)
    return encrypted_message


"""
function: aes_cbc_decrypt
input params:
    encrypted_message: encrypted message
    passphrase: passphrase is the key which can be 128, 192, or 256 bits (16, 24, or 32 bytes)
    IV: IV is used to mix up the output of a encryption when input is same, 
    so the IV is chosen as a random string, and use it as part of the encryption output, 
    and then use it to decrypt the message.
output params:
    returns decrypted message
"""


def aes_cbc_decrypt(encrypted_message, passphrase, iv):
    encrypted_message = b64decoding(encrypted_message)
    aes = AES.new(passphrase, AES.MODE_CBC, iv)
    plain_text = aes.decrypt(encrypted_message)
    encoder = PKCS7Encoder()
    return encoder.decode(plain_text)


"""
function: sign_data_with_hmac_sha256
input params:
    message: message which to be signed
    private_key: private key
output params:

returns signed message using SHA246
"""


def sign_data_with_hmac_sha256(message, private_key):
    try:
        dig = hmac.new(private_key, msg=message,
                       digestmod=hashlib.sha256).digest()
        return b64encoding(dig).decode()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("sign_data_with_hmac_sha256 %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: sign_encrypted_data_with_hmac_sha256
input params:
    message: encrypted message which to be signed
    private_key: private key
output params:

returns signed encrypted message using SHA246
"""


def sign_encrypted_data_with_hmac_sha256(message, private_key):
    temp_sha_256 = SHA256.new(message)
    signer = SignaturePKCS1_v1_5.new(private_key)
    signature = signer.sign(temp_sha_256)
    return b64encoding(signature)


"""
function: verify_signature_with_sha256
input params:
    public_key: public key
    message: message which to be verified
    signature: signature 
output params:
    True/False depending on whether signature valid or not by using SHA256
"""


def verify_signature_with_sha256(public_key, message, signature):
    temp_sha256 = SHA256.new(message)
    verifier = SignaturePKCS1_v1_5.new(public_key)
    if verifier.verify(temp_sha256, signature):
        return True
    else:
        return False


"""
function: generate_random_string_given_length
input params:
    len: length of the random string which to be generated
output params:

returns random string of given length
"""


def generate_random_string_given_length(len):
    return ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(len)])

"""
function: encrypt_long_text
input params:
    plain_long_text:long text string which to encrypted
    public_key_file: public key for encryption
output params:

returns encrypted long text string
"""


def encrypt_long_text(plain_long_text, public_key_file):

    global zlib, PKCS1_OAEP, base64

    public_key = import_key(open(public_key_file))
    plain_long_text = zlib.compress(plain_long_text)
    rsa_key = PKCS1_OAEP.new(public_key)

    chunk_size = 200
    offset = 0
    end_loop = False
    encrypted = ""

    while not end_loop:

        chunk = plain_long_text[offset:offset + chunk_size]

        if len(chunk) % chunk_size != 0:
            end_loop = True
            chunk += " " * (chunk_size - len(chunk))

        encrypted += rsa_key.encrypt(chunk)
        offset += chunk_size

    return base64.b64encode(encrypted)


"""
function: decrypt_long_text
input params:
    encrypted_long_text: long text string which to decrypted
    private_key_file: private key for decryption
output params:

returns decompressed decrypted long text string
"""


def decrypt_long_text(encrypted_long_text, private_key_file):

    global zlib, PKCS1_OAEP, base64

    private_key = import_key(open(private_key_file))
    rsa_key = PKCS1_OAEP.new(private_key)
    encrypted_long_text = base64.b64decode(encrypted_long_text)

    chunk_size = 256
    offset = 0
    decrypted = ""

    while offset < len(encrypted_long_text):
        chunk = encrypted_long_text[offset:offset + chunk_size]
        decrypted += rsa_key.decrypt(chunk)
        offset += chunk_size

    return zlib.decompress(decrypted)
