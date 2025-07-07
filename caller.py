# caller.py

import os
import sys
import json
import asyncio
from dotenv import load_dotenv

from livekit import api
from livekit.api.agent_dispatch_service import CreateAgentDispatchRequest

load_dotenv()

async def main(phone: str, context: str):
    # 1️⃣ Initialize the LiveKit management client (v1 API)
    client = api.LiveKitAPI(
        url=os.getenv("LIVEKIT_URL"),
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET"),
    )

    # 2️⃣ Build the dispatch request with your phone + context
    req = CreateAgentDispatchRequest(
        agent_name="heka-telephony-agent",   # must match your agent.py’s WorkerOptions.agent_name
        room="HekaRoom",
        metadata=json.dumps({
            "phone_number": phone,
            "context": context
        })
    )

    # 3️⃣ Send it off
    dispatch = await client.agent_dispatch.create_dispatch(req)
    print(f"✅ Dispatched agent → calling {phone} about “{context}” (dispatch_id: {dispatch.id})")

    # 4️⃣ Clean up
    await client.aclose()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python caller.py <phone_number> <context>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1], sys.argv[2]))
