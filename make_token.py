# make_token.py
import os
import time
import uuid
import jwt
from dotenv import load_dotenv

load_dotenv()

API_KEY    = os.getenv("LIVEKIT_API_KEY")
API_SECRET = os.getenv("LIVEKIT_API_SECRET")
ROOM       = os.getenv("LIVEKIT_ROOM", "HekaRoom")
IDENTITY   = "you-local"

now = int(time.time())
# Token valid for 1 hour
payload = {
    "jti": str(uuid.uuid4()),
    "iss": API_KEY,        # issuer
    "sub": IDENTITY,       # subject == identity
    "nbf": now,
    "exp": now + 3600,
    "grants": {
        "identity": IDENTITY,
        "video": {
            "room_join": True,
            "room": ROOM
        }
    }
}

token = jwt.encode(
    payload,
    API_SECRET,
    algorithm="HS256",
    headers={"alg": "HS256", "typ": "JWT"}
)

print(token)
