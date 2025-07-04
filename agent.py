# """
# LiveKit outbound-call smoke-test
# ────────────────────────────────
# • Places an outbound SIP call via LiveKit Cloud
# • Greets the callee, asks a yes/no question
# • Branches on reply, says goodbye, hangs up
# """

# import os, logging, asyncio
# from dotenv import load_dotenv
# from livekit.agents import (
#     Agent, AgentSession, JobContext, RoomInputOptions,
#     cli, WorkerOptions,
# )
# from livekit import api

# # ── plugin imports (current API) ───────────────────────────────
# from livekit.plugins.azure  import STT, TTS          # Azure Speech
# from livekit.plugins.silero import VAD              # Silero VAD
# from livekit.plugins.turn_detector.english import EnglishModel
# from livekit.plugins.openai import LLM              # OpenAI/Azure OpenAI
# # ───────────────────────────────────────────────────────────────

# # Load .env / .env.local
# if os.path.exists(".env.local"):
#     load_dotenv(".env.local")
# else:
#     load_dotenv()

# # Required env vars --------------------------------------------
# LIVEKIT_URL        = os.getenv("LIVEKIT_URL")          # wss://…livekit.cloud
# LIVEKIT_API_KEY    = os.getenv("LIVEKIT_API_KEY")
# LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
# SIP_TRUNK_ID       = os.getenv("SIP_OUTBOUND_TRUNK_ID")

# TEST_PHONE_NUMBER  = "+447388449042"   # 🔁 replace with your phone
# # --------------------------------------------------------------

# logging.basicConfig(level=logging.INFO)
# log = logging.getLogger("outbound-test")

# # ───────────────────────────────────────────────────────────────
# class OutboundBot(Agent):
#     """Minimal agent that lets AgentSession+LLM handle replies."""
#     async def on_message(self, ctx, message):
#         await ctx.session.generate_reply()

# async def entrypoint(ctx: JobContext):
#     """Worker entry: create call, start session, simple dialogue."""
#     await ctx.connect()

#     # ---------- voice / LLM pipeline ---------------------------
#     llm = LLM.with_azure(
#         model="gpt-4o-mini",
#         azure_endpoint   = os.getenv("AZURE_OPENAI_ENDPOINT"),
#         azure_deployment = "gpt-4o-mini",
#         api_version      = os.getenv("OPENAI_API_VERSION"),
#         api_key          = os.getenv("AZURE_OPENAI_API_KEY"),
#         #tool_choice      = "auto",
#     )
#     stt = STT(   # keys can also come purely from env vars
#         speech_key   = os.getenv("AZURE_SPEECH_KEY"),
#         speech_region= os.getenv("AZURE_SPEECH_REGION")
#     )
#     tts = TTS(
#         speech_key   = os.getenv("AZURE_SPEECH_KEY"),
#         speech_region= os.getenv("AZURE_SPEECH_REGION"),
#         voice        = "en-US-JennyNeural",
#     )
#     session = AgentSession(
#         #turn_detector = EnglishModel(),
#         turn_detection = EnglishModel(),
#         vad           = VAD.load(),      # download model on first run
#         stt           = stt,
#         llm           = llm,
#         tts           = tts,
#     )
#     bot = OutboundBot(instructions="You are a friendly outbound calling agent. Greet the user, ask the user's name and then ask them if they would like to be contacted by a human agent.")

#     # ---------- place outbound SIP call ------------------------
#     await ctx.api.sip.create_sip_participant(
#         api.CreateSIPParticipantRequest(
#             room_name            = ctx.room.name,
#             sip_trunk_id         = SIP_TRUNK_ID,
#             sip_call_to          = TEST_PHONE_NUMBER,
#             participant_identity = TEST_PHONE_NUMBER,
#             wait_until_answered  = True,
#         )
#     )
#     log.info("Dialling %s via trunk %s", TEST_PHONE_NUMBER, SIP_TRUNK_ID)

#     # ---------- run the interactive session --------------------
#     await session.start(
#         agent = bot,
#         room  = ctx.room,
#         room_input_options = RoomInputOptions()  # default noise-suppr.
#     )

#     await session.say(
#         "Hello! This is an automated test call from Heka Agent. "
#         "Can I ask you a quick question?"
#     )

#     # reply = await session.listen()
#     # log.info("User said: %r", reply.transcript)

#     # if "yes" in reply.transcript.lower():
#     #     await session.say("Great, thanks for confirming. Have a wonderful day!")
#     # else:
#     #     await session.say("No worries. Goodbye!")
#     async def on_message(self, ctx, message):
#         await ctx.session.generate_reply()


#     await session.end()   # hangs up + closes room
# # ───────────────────────────────────────────────────────────────

# if __name__ == "__main__":
#     cli.run_app(
#         WorkerOptions(
#             entrypoint_fnc = entrypoint,
#             agent_name     = "outbound-test-caller",
#         )
#     )

import os
import json
import logging
import asyncio
from dotenv import load_dotenv
from livekit.agents import Agent, AgentSession, JobContext, cli, WorkerOptions
from livekit import api
from livekit.plugins.azure import STT, TTS
from livekit.plugins.silero import VAD
from livekit.plugins.turn_detector.english import EnglishModel
from livekit.plugins.openai import LLM

if os.path.exists(".env.local"):
    load_dotenv(".env.local")
else:
    load_dotenv()

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
SIP_TRUNK_ID = os.getenv("SIP_OUTBOUND_TRUNK_ID")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("outbound-agent")

class OutboundBot(Agent):
    async def on_message(self, ctx, message):
        await ctx.session.generate_reply()

async def entrypoint(ctx: JobContext):
    await ctx.connect()

    # Setup voice + LLM pipeline
    llm = LLM.with_azure(
        model="gpt-4o-mini",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment="gpt-4o-mini",
        api_version=os.getenv("OPENAI_API_VERSION"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY")
    )
    stt = STT(speech_key=os.getenv("AZURE_SPEECH_KEY"),
              speech_region=os.getenv("AZURE_SPEECH_REGION"))
    tts = TTS(speech_key=os.getenv("AZURE_SPEECH_KEY"),
              speech_region=os.getenv("AZURE_SPEECH_REGION"),
              voice="en-US-JennyNeural")
    session = AgentSession(
        turn_detection=EnglishModel(),
        vad=VAD.load(),
        stt=stt,
        llm=llm,
        tts=tts
    )
    bot = OutboundBot(instructions=(
        "You are a friendly outbound calling agent. "
        "Greet the user, ask their name, and ask if they want to speak to a human."
    ))

    data = ctx.job.metadata or "{}"
    info = json.loads(data)
    phone = info.get("phone_number")
    topic = info.get("topic", "a quick call")

    if phone:
        await ctx.api.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                room_name=ctx.room.name,
                sip_trunk_id=SIP_TRUNK_ID,
                sip_call_to=phone,
                participant_identity=phone,
                wait_until_answered=True
            )
        )
        log.info("Dialing %s via trunk %s", phone, SIP_TRUNK_ID)

    await session.start(agent=bot, room=ctx.room,
                        room_input_options=None)

    await session.say(
        f"Hello! This is an automated call regarding {topic}. May I ask you a quick question?"
    )

    reply = await session.listen()
    log.info("User replied: %r", reply.transcript)

    if reply.transcript and "yes" in reply.transcript.lower():
        await session.say("Fantastic! Thank you for your time. Goodbye!")
    else:
        await session.say("Alright, maybe another time. Goodbye!")

    await session.end()

if __name__ == "__main__":
    opts = WorkerOptions(
        entrypoint_fnc=entrypoint,
        agent_name="outbound-telephony-agent"
    )
    cli.run_app(opts)
