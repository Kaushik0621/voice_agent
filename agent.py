
# import os
# import json
# import sys
# import asyncio
# import random
# import time
# from dotenv import load_dotenv

# from livekit.agents.cli import run_app
# from livekit.agents import JobContext, WorkerOptions, AutoSubscribe
# from livekit.agents.voice import AgentSession, Agent
# from livekit.api.sip_service import CreateSIPParticipantRequest
# from livekit.plugins.azure.stt import STT as AzureSTT
# from livekit.plugins.azure.tts import TTS as AzureTTS
# from livekit.plugins.openai import LLM as OpenAILLM
# from livekit.plugins.silero.vad import VAD as SileroVAD

# # Load environment variables
# dotenv_path = os.getenv("DOTENV_PATH")
# load_dotenv(dotenv_path if dotenv_path else None)

# # Enhanced instructions for natural speech
# NATURAL_SPEECH_INSTRUCTIONS = """
# You are a friendly, helpful assistant named Heka. Speak naturally with occasional conversational fillers like 
# "um", "uh", "you know", "like", "actually", and "I mean" to sound more human. Use short pauses between thoughts 
# represented by commas and periods. Keep responses concise but add natural variations in pacing.

# Examples of natural responses:
# - "Hmm, let me think about that for a moment..."
# - "Okay, so what you're asking is... uh... about the weather?"
# - "Well, actually, I believe the forecast says..."
# - "You know, I think we should consider..."
# - "Right, so to answer your question..."

# Focus on creating natural, flowing conversation rather than perfectly structured responses.
# """

# # Initialize LLM with natural speech instructions
# llm = OpenAILLM.with_azure(
#     azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
#     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
#     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#     api_version=os.getenv("OPENAI_API_VERSION"),
# )

# async def generate_natural_response(text: str):
#     """Generate a natural-sounding response with conversational fillers"""
#     # Simulate thinking time
#     await asyncio.sleep(random.uniform(1.0, 3.0))
    
#     # Get LLM response with natural speech patterns
#     response = await llm.chat(
#         messages=[
#             {"role": "system", "content": NATURAL_SPEECH_INSTRUCTIONS},
#             {"role": "user", "content": text}
#         ],
#         max_tokens=200,
#     )
    
#     return response

# async def entrypoint(ctx: JobContext):
#     await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

#     meta = json.loads(ctx.job.metadata or "{}")
#     phone = meta.get('phone_number')
#     topic = meta.get('context', 'this call')

#     # Initialize plugins
#     stt = AzureSTT(
#         speech_key=os.getenv('AZURE_SPEECH_KEY'),
#         speech_region=os.getenv('AZURE_SPEECH_REGION'),
#     )
#     tts = AzureTTS(
#         speech_key=os.getenv('AZURE_SPEECH_KEY'),
#         speech_region=os.getenv('AZURE_SPEECH_REGION'),
#         voice="en-US-JennyNeural"
#     )
    
#     # Initialize VAD
#     vad = SileroVAD.load()

#     opening_line = "Hi, this is Heka speaking. How can I assist you today?"
#     fallback_line = "Are you still there? Let me know if I can help with anything."

#     if phone:
#         await ctx.api.sip.create_sip_participant(
#             CreateSIPParticipantRequest(
#                 room_name=ctx.room.name,
#                 sip_trunk_id=os.getenv('SIP_OUTBOUND_TRUNK_ID'),
#                 sip_call_to=phone,
#                 participant_identity=phone,
#                 wait_until_answered=True,
#             )
#         )
#         print(f"📞 Calling {phone} about '{topic}'... connected")

#     # Create agent session
#     session = AgentSession(
#         stt=stt,
#         llm=llm,
#         tts=tts,
#         vad=vad,
#     )

#     # Start session
#     await session.start(
#         room=ctx.room,
#         agent=Agent(instructions=NATURAL_SPEECH_INSTRUCTIONS),
#     )

#     # Initial greeting
#     await session.say(opening_line)

#     # Main conversation loop
#     last_activity = time.time()
#     while True:
#         try:
#             # Wait for transcript event using documented approach
#             # Create a future to wait for the next transcript
#             transcript_future = asyncio.Future()
            
#             def on_transcript(event):
#                 if not transcript_future.done():
#                     transcript_future.set_result(event)
            
#             session.on("transcript_received", on_transcript)
            
#             try:
#                 # Wait for either transcript or timeout
#                 event = await asyncio.wait_for(transcript_future, timeout=10)
#                 last_activity = time.time()
                
#                 # Generate natural response with fillers
#                 response = await generate_natural_response(event.transcript)
#                 print(f"🗣️ Response: {response}")
#                 await session.say(response)
                
#             except asyncio.TimeoutError:
#                 # Remove the event listener if no transcript was received
#                 session.off("transcript_received", on_transcript)
                
#                 # Check for inactivity
#                 if time.time() - last_activity > 15:
#                     await session.say(fallback_line)
#                     last_activity = time.time()
            
#         except Exception as e:
#             print(f"Error: {e}")
#             break

#     # Properly end the session
#     await session.end()

# if __name__ == '__main__':
#     if len(sys.argv) == 1:
#         sys.argv.append('dev')
#     run_app(
#         WorkerOptions(
#             entrypoint_fnc=entrypoint,
#             agent_name='heka-telephony-agent'
#         )
#     )
import os
import json
import sys
import asyncio
import random
import time
from dotenv import load_dotenv

from livekit.agents.cli import run_app
from livekit.agents import JobContext, WorkerOptions, AutoSubscribe
from livekit.agents.voice import AgentSession, Agent
from livekit.api.sip_service import CreateSIPParticipantRequest

from livekit.plugins.azure.stt import STT as AzureSTT
from livekit.plugins.azure.tts import TTS as AzureTTS
from livekit.plugins.openai import LLM as OpenAILLM
from livekit.plugins.silero.vad import VAD as SileroVAD
from livekit.plugins import elevenlabs


# Load environment variables
dotenv_path = os.getenv("DOTENV_PATH")
load_dotenv(dotenv_path if dotenv_path else None)



# Enhanced instructions for natural speech
NATURAL_SPEECH_INSTRUCTIONS = """
You are a friendly, helpful assistant named Heka. Speak naturally with occasional conversational fillers like 
"um", "uh", "you know", "like", "actually", and "I mean" to sound more human. Use short pauses between thoughts 
represented by commas and periods. Keep responses concise but add natural variations in pacing.

Examples of natural responses:
- "Hmm, let me think about that for a moment..."
- "Okay, so what you're asking is... uh... about the weather?"
- "Well, actually, I believe the forecast says..."
- "You know, I think we should consider..."
- "Right, so to answer your question..."

Focus on creating natural, flowing conversation rather than perfectly structured responses.
"""

# Initialize LLM with natural speech instructions
llm = OpenAILLM.with_azure(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
)

async def generate_natural_response(text: str):
    """Generate a natural-sounding response with conversational fillers"""
    # Simulate thinking time
    await asyncio.sleep(random.uniform(1.0, 3.0))
    
    # Get LLM response with natural speech patterns
    response = await llm.chat(
        messages=[
            {"role": "system", "content": NATURAL_SPEECH_INSTRUCTIONS},
            {"role": "user", "content": text}
        ],
        max_tokens=200,
    )
    
    return response

async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    meta = json.loads(ctx.job.metadata or "{}")
    phone = meta.get('phone_number')
    topic = meta.get('context', 'this call')

    # Initialize STT
    stt = AzureSTT(
        speech_key=os.getenv('AZURE_SPEECH_KEY'),
        speech_region=os.getenv('AZURE_SPEECH_REGION'),
    )

    # Initialize ElevenLabs TTS (inspired by your previous integration)
    # tts = CustomAzureTTS(
    #     speech_key=os.getenv("AZURE_SPEECH_KEY"),
    #     speech_region=os.getenv("AZURE_SPEECH_REGION"),
    #     voice="en-US-AriaNeural"
    #     )
    # tts = AzureTTS(
    #     speech_key=os.getenv('AZURE_SPEECH_KEY'),
    #     speech_region=os.getenv('AZURE_SPEECH_REGION'),
    #     voice="en-US-JennyNeural"
    # )
    tts = elevenlabs.TTS(
        api_key=os.getenv("ELEVEN_API_KEY"),
        voice_id="EXAVITQu4vr4xnSDxMaL",  # Default known working voice
        #voice_id="pBZVCk298iJlHAcHQwLr",
        model="eleven_multilingual_v2",
        streaming_latency=1,
        #streaming_latency=int(os.getenv("ELEVEN_STREAMING_LATENCY", "1")),
    )
    
    # Initialize VAD
    vad = SileroVAD.load()

    opening_line = "Hi, this is your assistant speaking. you wanted me to call you. How can I assist you today?"
    fallback_line = "Are you still there? Let me know if I can help with anything."

    if phone:
        await ctx.api.sip.create_sip_participant(
            CreateSIPParticipantRequest(
                room_name=ctx.room.name,
                sip_trunk_id=os.getenv('SIP_OUTBOUND_TRUNK_ID'),
                sip_call_to=phone,
                participant_identity=phone,
                wait_until_answered=True,
            )
        )
        print(f"📞 Calling {phone} about '{topic}'... connected")

    # Create agent session
    session = AgentSession(
        stt=stt,
        llm=llm,
        tts=tts,
        vad=vad,
    )

    # Start session
    await session.start(
        room=ctx.room,
        agent=Agent(instructions=NATURAL_SPEECH_INSTRUCTIONS),
    )

    # Initial greeting
    await session.say(opening_line)

    # Main conversation loop
    last_activity = time.time()
    while True:
        try:
            transcript_future = asyncio.Future()
            def on_transcript(event):
                if not transcript_future.done():
                    transcript_future.set_result(event)
            session.on("transcript_received", on_transcript)
            
            try:
                event = await asyncio.wait_for(transcript_future, timeout=10)
                last_activity = time.time()
                
                response = await generate_natural_response(event.transcript)
                print(f"🗣️ Response: {response}")
                await session.say(response)
                
            except asyncio.TimeoutError:
                session.off("transcript_received", on_transcript)
                if time.time() - last_activity > 25:
                    await session.say(fallback_line)
                    last_activity = time.time()
            
        except Exception as e:
            print(f"Error: {e}")
            break

    await session.end()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        sys.argv.append('dev')
    run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name='heka-telephony-agent'
        )
    )
