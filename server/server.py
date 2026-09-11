# this is the main file on server
import json
import uuid
import config
from crypto import (
    decrypt_payload,
    derive_shared_aes_key,
    encrypt_payload,
    generate_keypair,
)
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
import helper
from pydantic import BaseModel
import uvicorn

if config.first_time:
    helper.generate_server_code()
else:
    if config.DEBUG:
        print("SERVER ID ALREADY GENERATED SKIPPING..")

app = FastAPI()
sessions = {}


@app.middleware("http")
async def crypto_middleware(request: Request, call_next):
    if request.url.path in [
        "/api/handshake",
        "/docs",
        "/openapi.json",
        "/redoc",
    ]:
        return await call_next(request)

    session_id = request.headers.get("X-Session-ID")
    if not session_id or session_id not in sessions:
        return JSONResponse(status_code=401, content={"detail": "Invalid session"})

    aes_key = sessions[session_id]

    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
        if body:
            try:
                raw_json = json.loads(body)
                if "data" in raw_json:
                    decrypted_dict = decrypt_payload(
                        aes_key, raw_json["data"]
                    )
                    decrypted_body_bytes = json.dumps(decrypted_dict).encode(
                        "utf-8"
                    )

                    request._body = decrypted_body_bytes

                    if hasattr(request, "_json"):
                        delattr(request, "_json")

                    async def receive():
                        return {
                            "type": "http.request",
                            "body": decrypted_body_bytes,
                            "more_body": False,
                        }

                    request._receive = receive

            except Exception as e:
                return JSONResponse(
                    status_code=400,
                    content={"detail": f"Decryption error: {str(e)}"},
                )

    response = await call_next(request)

    # Шифрование исходящего ответа
    if response.status_code == 200 and "application/json" in response.headers.get(
        "content-type", ""
    ):
        response_body = [section async for section in response.body_iterator]
        raw_res = json.loads(b"".join(response_body).decode())

        encrypted_res = encrypt_payload(aes_key, raw_res)
        return JSONResponse(
            status_code=response.status_code, content={"data": encrypted_res}
        )

    return response


class HandshakeDTO(BaseModel):
    public_key: str


@app.post("/api/handshake")
def handshake(dto: HandshakeDTO):
    priv_key, pub_b64 = generate_keypair()
    aes_key = derive_shared_aes_key(priv_key, dto.public_key)

    session_id = str(uuid.uuid4())
    sessions[session_id] = aes_key
    return {"session_id": session_id, "server_public_key": pub_b64}


#base endpoints

class MessageDTO(BaseModel):
    channel_id: int
    text: str



@app.post("/channels/messages")
def send_message(msg: MessageDTO):
    print(f"Новое сообщение в канале {msg.channel_id}: {msg.text}")
    return {"id": 101, "status": "delivered", "text": msg.text}


@app.post("/channels/create")
def create_channel(data: dict):
    return {"created": True, "name": data.get("name")}


@app.post("/api/auth/login")
def auth_login(data: dict):
    return {"status": "ok", "token": "dummy_token"}


@app.post("/api/auth/check_login")
def auth_check_login(data: dict):
    return {"exists": False}


@app.post("/api/auth/register")
def auth_register(data: dict):
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(config.server_api_port) if config.server_api_port else 19840
    uvicorn.run(app, host="0.0.0.0", port=port)