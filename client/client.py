### here will be api calls
import base64
import json
import os
import random
import string
import config
from crypto import (
    decrypt_payload,
    derive_shared_aes_key,
    encrypt_payload,
    generate_keypair,
)
import requests


class SecureClient:

    def __init__(self, base_url: str = ""):
        self.base_url = base_url.rstrip("/") if base_url else ""
        self.session = requests.Session()
        self.session_id = None
        self.aes_key = None

    def set_base_url(self, url: str):
        self.base_url = url.rstrip("/")
        self.session_id = None
        self.aes_key = None

    def _handshake(self):
        if not self.base_url:
            raise ValueError("no url")

        priv_key, pub_b64 = generate_keypair()
        res = self.session.post(
            f"{self.base_url}/api/handshake",
            json={"public_key": pub_b64},
            timeout=5,
        )
        res.raise_for_status()
        data = res.json()

        self.session_id = data["session_id"]
        self.aes_key = derive_shared_aes_key(priv_key, data["server_public_key"])
        if config.DEBUG:
            print(f"Hs good session_id: {self.session_id}")

    def post(self, endpoint: str, json_data: dict = None, **kwargs):
        return self._request("POST", endpoint, json_data=json_data, **kwargs)

    def get(self, endpoint: str, **kwargs):
        return self._request("GET", endpoint, **kwargs)

    def _request(
        self,
        method: str,
        endpoint: str,
        json_data: dict = None,
        _retry: bool = False,
        **kwargs,
    ):
        if not self.aes_key:
            self._handshake()

        headers = kwargs.pop("headers", {})
        headers["X-Session-ID"] = self.session_id

        body = None
        if json_data is not None:
            encrypted_data = encrypt_payload(self.aes_key, json_data)
            body = {"data": encrypted_data}

        url = f"{self.base_url}{endpoint}"
        response = self.session.request(
            method, url, json=body, headers=headers, **kwargs
        )


        if response.status_code == 401 and not _retry:
            if config.DEBUG:
                print("[!] Сессия устарела. Переподключение и повтор запроса...")
            self._handshake()
            return self._request(
                method, endpoint, json_data=json_data, _retry=True, **kwargs
            )

        if response.ok and response.text:
            try:
                res_json = response.json()
                if isinstance(res_json, dict) and "data" in res_json:
                    return decrypt_payload(self.aes_key, res_json["data"])
                return res_json
            except Exception:
                return response.json()

        return response.json()


client = SecureClient()


if config.server_domain:
    protocol = (
        "http"
        if config.TESTING or config.server_domain in ["127.0.0.1", "localhost"]
        else "https"
    )
    client.set_base_url(
        f"{protocol}://{config.server_domain}:{config.server_api_port}"
    )


def save_config(inst, val):
    setattr(config, inst, val)
    with open("config.py", "w", encoding="utf-8") as f:
        for k, v in vars(config).items():
            if not k.startswith("__"):
                f.write(f"{k} = {repr(v)}\n")


def uid_generator(size=20, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


def make_user_data_first_time(display_name, login, email, description, avatar_url, connected_server):
    uid = uid_generator()
    os.makedirs("udata", exist_ok=True)
    os.makedirs(config.user_download_path, exist_ok=True)

    user_data = {
        "uid": uid,
        "login": login,
        "email": email,
        "display_name": display_name,
        "description": description,
        "avatar_url": avatar_url,
        "connected_server": connected_server,
        "settings": {
            "theme": "dark",
            "language": "en",
            "notifications": {
                "sound_enabled": True,
                "desktop_alerts": True,
                "show_preview": True,
            },
            "privacy": {
                "show_online_status": True,
                "send_read_receipts": True,
            },
        },
        "chat_state": {
            "pinned_chats": [],
            "muted_chats": [],
            "archived_chats": [],
            "blocked_uids": [],
        },
        "device": {
            "platform": "desktop",
            "app_version": "0.0.1",
        },
    }

    with open("udata/UserData.json", "w", encoding="utf-8") as ufile:
        ufile.write(json.dumps(user_data))
    with open("udata/UserDM.json", "w", encoding="utf-8") as udmfile:
        udmfile.write("[]")
    with open("udata/UserGroups.json", "w", encoding="utf-8") as ugfile:
        ugfile.write("[]")


def decode_server_key(key):
    key_bytes = key.encode("ascii")
    key_string_bytes = base64.b64decode(key_bytes)
    key_decoded = key_string_bytes.decode("ascii")
    return key_decoded


def check_server_availability(key):
    try:
        decode_result = decode_server_key(key)
        server_info = json.loads(decode_result)
        s_domain = server_info["domain"]
        s_port = server_info["port"]
        s_pub_gr = server_info["pub_group"]

        save_config("server_key", key)
        save_config("server_domain", s_domain)
        save_config("server_api_port", s_port)
        save_config("pub_server_group_id", s_pub_gr)

        protocol = (
            "http" if config.TESTING or s_domain in ["127.0.0.1", "localhost"] else "https"
        )
        client.set_base_url(f"{protocol}://{s_domain}:{s_port}")

        client._handshake()
        return True
    except Exception as e:
        if config.DEBUG:
            print(f"Server check faild: {e}")
        return False


def login(login_val, password_val):
    if config.TESTING and login_val == "tester" and password_val == "12345":
        return True

    res = client.post(
        "/api/auth/login", {"login": login_val, "password": password_val}
    )
    return res.get("status") == "ok"


def check_reg(login_val):
    res = client.post("/api/auth/check_login", {"login": login_val})
    return res.get("exists", False)


def register(login_val, password_val):
    res = client.post(
        "/api/auth/register", {"login": login_val, "password": password_val}
    )
    return res.get("status") == "ok"