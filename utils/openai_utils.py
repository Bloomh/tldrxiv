import openai
import os
import io
from pathlib import Path

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def text_to_speech(podcast_script: str):
    with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="coral",
            input=podcast_script,
            instructions="Speak in an academic tone and pace, focusing on clarity and pronunciation.",
    ) as response:
        audio_data = io.BytesIO()

        # Iterate over the response chunks and write them to the BytesIO object
        for chunk in response.iter_bytes():
            audio_data.write(chunk)

        # Return the audio data
        audio_data.seek(0)  # Reset the stream position to the beginning

        return audio_data.read()
