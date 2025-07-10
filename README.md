create a new env
set the .env file like this 

#LiveKit
LIVEKIT_URL=
LIVEKIT_API_KEY=
LIVEKIT_API_SECRET=

# LIVEKIT_URL=
# LIVEKIT_API_KEY=
# LIVEKIT_API_SECRET=
# LIVEKIT_ROOM=
# SIP
SIP_OUTBOUND_TRUNK_ID=

# Azure Speech
AZURE_SPEECH_KEY=
AZURE_SPEECH_REGION=

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_DEPLOYMENT=
OPENAI_API_VERSION=

# ElevenLabs TTS
# ELEVEN_API_KEY=
# VOICE_ID=
ELEVEN_API_KEY=
VOICE_ID=


after that install the libs
Pip install -r requirements.txt

start 2 console
1st console
python agent.py dev
2nd console
python caller.py +44...... "topic"
