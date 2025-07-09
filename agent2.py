# agent.py
import os, json, random, asyncio
from dotenv import load_dotenv

from livekit.agents.cli import run_app
from livekit.agents import JobContext, WorkerOptions, AutoSubscribe
from livekit.agents.voice import AgentSession, Agent
from livekit.plugins.azure.stt import STT as AzureSTT
from livekit.plugins.azure.tts import TTS as AzureTTS
from livekit.plugins.openai import LLM as OpenAILLM
from livekit.plugins.silero.vad import VAD as SileroVAD

load_dotenv()

# 1️⃣ Create your LLM client
llm = OpenAILLM.with_azure(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
)

async def entrypoint(ctx: JobContext):
    # Connect for audio
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    meta     = json.loads(ctx.job.metadata or "{}")
    simulate = meta.get("simulate", False)
    print("🔁 Running in", "SIMULATION" if simulate else "REAL-CALL", "mode")

    # 2️⃣ Init STT, TTS, VAD
    stt = AzureSTT()      # reads KEY & REGION from env
    tts = AzureTTS()      # same
    vad = SileroVAD.load()  # we’ll only use this for future enhancements

    session = AgentSession(stt=stt, llm=llm, tts=tts, vad=vad)

    # 3️⃣ Silent fallback after 6s
    async def fallback():
        await asyncio.sleep(6)
        await session.say("Are you still there?")
    asyncio.create_task(fallback())

    # 4️⃣ Start the voice loop
    await session.start(
        room=ctx.room,
        agent=Agent(instructions="You are a friendly assistant. Speak naturally.")
    )

    # 5️⃣ Opening line
    await session.say("Hi, this is Heka. How can I assist you today?")

if __name__ == "__main__":
    run_app(WorkerOptions(entrypoint_fnc=entrypoint, agent_name="heka-telephony-agent"))
