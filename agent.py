import os
import json
import sys
from dotenv import load_dotenv

from livekit.agents.cli import run_app
from livekit.agents import JobContext, WorkerOptions, AutoSubscribe
from livekit.agents.voice import AgentSession, Agent
from livekit.api.sip_service import CreateSIPParticipantRequest

from livekit.plugins.azure.stt import STT as AzureSTT
from livekit.plugins.openai import LLM as OpenAILLM
from livekit.plugins.silero.vad import VAD as SileroVAD
from livekit.plugins import elevenlabs

load_dotenv()

# Configure Azure OpenAI
llm = OpenAILLM.with_azure(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
)

async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    meta = json.loads(ctx.job.metadata or "{}")
    phone = meta.get("phone_number")
    topic = meta.get("context", "this call")

    if phone:
        await ctx.api.sip.create_sip_participant(
            CreateSIPParticipantRequest(
                room_name=ctx.room.name,
                sip_trunk_id=os.getenv("SIP_OUTBOUND_TRUNK_ID"),
                sip_call_to=phone,
                participant_identity=phone,
                wait_until_answered=True,
            )
        )
        print(f" Calling {phone} about \"{topic}\"... connected")

    stt = AzureSTT(
        speech_key=os.getenv("AZURE_SPEECH_KEY"),
        speech_region=os.getenv("AZURE_SPEECH_REGION"),
    )

    tts = elevenlabs.TTS(
        api_key=os.getenv("ELEVEN_API_KEY"),
        voice_id="EXAVITQu4vr4xnSDxMaL",  # Default known working voice
        model="eleven_multilingual_v2",
        streaming_latency=1,
    )

    session = AgentSession(
        stt=stt,
        llm=llm,
        tts=tts,
        vad=SileroVAD.load()
    )

    await session.start(
        room=ctx.room,
        agent=Agent(instructions="You are a friendly assistant that greets the user and has a natural conversation."),
        room_input_options=None,
    )

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append("dev")

    run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="heka-telephony-agent",
        )
    )