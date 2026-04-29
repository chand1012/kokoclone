import tempfile
from typing import Optional

from cog import BasePredictor, Input, Path


class Predictor(BasePredictor):
    def setup(self) -> None:
        """Load KokoClone models into memory once so predictions are fast."""
        from core.cloner import KokoClone

        self.cloner = KokoClone()

    def predict(
        self,
        mode: str = Input(
            description="Operation mode: 'tts' synthesizes text into cloned speech; 'convert' re-voices an existing audio recording.",
            choices=["tts", "convert"],
            default="tts",
        ),
        text: str = Input(
            description="[TTS mode] Text to synthesize into speech.",
            default=None,
        ),
        lang: str = Input(
            description="[TTS mode] Language of the input text.",
            choices=["en", "hi", "fr", "ja", "zh", "it", "es", "pt"],
            default="en",
        ),
        reference_audio: Path = Input(
            description="Reference voice sample (3–10 seconds of clean speech). The generated output will match this voice."
        ),
        source_audio: Optional[Path] = Input(
            description="[Convert mode] Source speech recording to re-voice. Not required for TTS mode.",
            default=None,
        ),
    ) -> Path:
        """
        Run a single prediction.

        - **TTS mode**: synthesizes `text` in `lang`, then clones the voice from `reference_audio`.
        - **Convert mode**: re-voices `source_audio` to sound like the speaker in `reference_audio`.
        """
        output_path = Path(tempfile.mktemp(suffix=".wav"))

        if mode == "tts":
            if not text or not text.strip():
                raise ValueError("'text' is required and must not be empty when mode is 'tts'.")
            self.cloner.generate(
                text=text,
                lang=lang,
                reference_audio=str(reference_audio),
                output_path=str(output_path),
            )
        else:  # convert
            if source_audio is None:
                raise ValueError("'source_audio' is required when mode is 'convert'.")
            self.cloner.convert(
                source_audio=str(source_audio),
                reference_audio=str(reference_audio),
                output_path=str(output_path),
            )

        return output_path
