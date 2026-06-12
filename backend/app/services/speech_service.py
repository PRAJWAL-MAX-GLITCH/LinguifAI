import logging
import uuid
from pathlib import Path

import openai
from fastapi import UploadFile

from app.core.config import settings

logger = logging.getLogger(__name__)


class SpeechService:
    """Service handling OpenAI Whisper for STT and OpenAI TTS for speech generation."""

    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.storage_dir = Path(settings.FILE_STORAGE_PATH) / "audio"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    async def transcribe_audio(self, file: UploadFile) -> str:
        """
        Save uploaded audio, send to OpenAI Whisper for transcription, and cleanup.
        """
        # Save temp file for Whisper
        temp_path = self.storage_dir / f"temp_{uuid.uuid4()}_{file.filename}"
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)

        logger.info("Transcribing audio file: %s", temp_path.name)

        try:
            with open(temp_path, "rb") as audio_file:
                response = await self.client.audio.transcriptions.create(
                    model=settings.WHISPER_MODEL,
                    file=audio_file,
                )
            return response.text
        except Exception as exc:
            logger.error("Whisper transcription failed: %s", exc)
            raise
        finally:
            if temp_path.exists():
                temp_path.unlink()

    async def synthesize_speech(self, text: str, voice: str = None) -> Path:
        """
        Generate spoken audio from text using OpenAI TTS.
        Saves the file to disk and returns the Path.
        """
        target_voice = voice or settings.TTS_VOICE
        output_filename = f"tts_{uuid.uuid4()}.mp3"
        output_path = self.storage_dir / output_filename

        logger.info("Synthesizing speech: %s -> %s", target_voice, output_filename)

        try:
            response = await self.client.audio.speech.create(
                model=settings.TTS_MODEL,
                voice=target_voice,
                input=text,
            )
            # Write to disk
            with open(output_path, "wb") as f:
                f.write(response.content)
            return output_path
        except Exception as exc:
            logger.error("TTS synthesis failed: %s", exc)
            raise
