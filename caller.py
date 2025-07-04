import sys
import asyncio
import json
import os
from dotenv import load_dotenv
from livekit import api

if os.path.exists(".env.local"):
    load_dotenv(".env.local")

async def make_call(phone_number: str, topic: str):
    lkapi = api.LiveKitAPI(
        os.getenv("LIVEKIT_URL"),
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET")
    )

    # 1️⃣ Create (or reuse) the room
    room = await lkapi.room.create_room(api.CreateRoomRequest(name="outbound-call-room"))

    # 2️⃣ Dispatch the agent to this room with metadata
    metadata = json.dumps({"phone_number": phone_number, "topic": topic})
    dispatch = await lkapi.agent_dispatch.create_dispatch(
        api.CreateAgentDispatchRequest(
            agent_name="outbound-telephony-agent",
            room=room.name,
            metadata=metadata
        )
    )
    print(f"🚀 Dispatched agent with dispatch ID {dispatch.id} to call {phone_number} about '{topic}'")

    await lkapi.aclose()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python caller.py <phone_number> <topic>")
        sys.exit(1)
    asyncio.run(make_call(sys.argv[1], sys.argv[2]))
