

import asyncio
import json
import base64
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import numpy as np
import requests
# from pydub import AudioSegment

app = FastAPI()

TTS_SERVER_URL = "https://backpy.robin-ai.xyz:5056"
STREAM_CHUNK_SIZE = 20

@app.websocket("/realtime-ai")
async def realtime_ai_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected to custom AI server")

    try:
        async for message in websocket.iter_text():
            data = json.loads(message)
            
            if data['type'] == 'input_audio_buffer.append':
                print("Stream opened")
                # Simulate processing audio (convert base64 -> fake transcript)
                raw_audio = base64.b64decode(data['audio'])
                transcript = fake_speech_to_text(raw_audio)
                
                # Convert transcript to speech
                transcript = "Mensaje de prueba"
                tts_audio = text_to_speech(transcript)
                
                response_event = {
                    "type": "response.audio.delta",
                     "delta": base64.b64encode(tts_audio).decode('utf-8') if tts_audio else ""
                }
                await websocket.send_json(response_event)
                print("Sent processed audio response")
    
    except WebSocketDisconnect:
        print("Client disconnected")


def fake_speech_to_text(audio_bytes):
    """Simulates speech-to-text processing."""
    return "Entiendo lo que dices pero esto es una respuesta de test"



import subprocess

def convert_to_g711_ulaw(audio_chunk, sample_rate=8000):
    """Convierte un chunk de audio PCM a G.711 u-law (PCMU)"""
    process = subprocess.Popen(
        [
            "ffmpeg", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", "-",
            "-ar", str(sample_rate), "-ac", "1", "-acodec", "pcm_mulaw", "-f", "mulaw", "-"
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )
    pcm_mulaw_audio, _ = process.communicate(audio_chunk)
    return pcm_mulaw_audio


def convert_to_g711_ulaw_sox(audio_chunk, sample_rate=8000):
    """Convierte un chunk de audio PCM a G.711 u-law usando sox"""
    tfm = sox.Transformer()
    tfm.rate(sample_rate)
    tfm.channels(1)
    tfm.output_format(file_type="ulaw")

    return tfm.build_array(input_array=np.frombuffer(audio_chunk, dtype=np.int16), sample_rate_in=24000).tobytes()


import numpy as np

def linear_to_mulaw(audio_chunk, mu=255):
    """Convierte audio PCM lineal (16-bit) a G.711 u-law (PCMU)"""
    # Convertir el buffer a un array de enteros de 16 bits
    audio_chunk = np.frombuffer(audio_chunk, dtype=np.int16)

    # Aplicar la fórmula oficial de u-law
    mu = np.float32(mu)
    sign = np.sign(audio_chunk)
    magnitude = np.log1p(mu * np.abs(audio_chunk) / 32768.0) / np.log1p(mu)
    ulaw_audio = (sign * magnitude * 127.0).astype(np.int8)

    return ulaw_audio.tobytes()




FAKE = False
def text_to_speech(text):
    """Consume el servicio TTS y devuelve audio en base64."""
    if FAKE:
        return np.random.bytes(320)  # Simulated 20ms G711 encoded audio
    with open("./wgwebsockets/default_speaker.json", "r") as file:
        speaker_params = json.load(file)
    payload = {
        "text": text,
        "language": "es",
        "stream_chunk_size": STREAM_CHUNK_SIZE,
        **speaker_params
    }
    res = requests.post(f"{TTS_SERVER_URL}/tts_stream_wav", json=payload)
    print('ApiResponse')
    print(res)
    if res.status_code != 200:
        return None
    print(type(res.content))
    #return linear_to_mulaw(res.content)
    return convert_to_g711_ulaw(res.content)




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7070)


