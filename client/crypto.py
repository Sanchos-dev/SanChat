import base64
import json
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

def generate_keypair():
    private_key = x25519.X25519PrivateKey.generate()
    public_key = private_key.public_key()
    pub_bytes = public_key.public_bytes_raw()
    return private_key, base64.b64encode(pub_bytes).decode("utf-8")

def derive_shared_aes_key(
    private_key, peer_public_key_b64: str, info: bytes = b"handshake"
) -> bytes:
    peer_bytes = base64.b64decode(peer_public_key_b64)
    peer_pub = x25519.X25519PublicKey.from_public_bytes(peer_bytes)
    shared_secret = private_key.exchange(peer_pub)
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=info,
    ).derive(shared_secret)

def encrypt_payload(aes_key: bytes, data: dict) -> str:
    raw_json = json.dumps(data).encode("utf-8")
    nonce = os.urandom(12)
    ciphertext = AESGCM(aes_key).encrypt(nonce, raw_json, None)
    return base64.b64encode(nonce + ciphertext).decode("utf-8")

def decrypt_payload(aes_key: bytes, encrypted_b64: str) -> dict:
    raw = base64.b64decode(encrypted_b64)
    nonce = raw[:12]
    ciphertext = raw[12:]
    decrypted_bytes = AESGCM(aes_key).decrypt(nonce, ciphertext, None)
    return json.loads(decrypted_bytes.decode("utf-8"))