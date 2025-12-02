from piper import PiperVoice, SynthesisConfig
import simpleaudio as sa
import wave
import os
import uuid
import threading


class TextToSpeech:
    def __init__(self):
        """Load the Piper model once."""
        self.voice = PiperVoice.load("data/tts_model/en_US-hfc_female-medium.onnx")

        self.syn_config = SynthesisConfig(
            volume=0.5,           # 50% volume
            length_scale=1.0,     # 1.0 = normal speed
            noise_scale=1.0,      
            noise_w_scale=1.0,    
            normalize_audio=False
        )

        # Ensure output directory exists
        self.audio_dir = "data/audio"
        os.makedirs(self.audio_dir, exist_ok=True)

    def _play_async(self, filepath: str):
        """Play audio in a background thread."""
        try:
            wave_obj = sa.WaveObject.from_wave_file(filepath)
            play_obj = wave_obj.play()
            play_obj.wait_done()
        finally:
            # Remove audio after playback
            if os.path.exists(filepath):
                os.remove(filepath)

    def Speech(self, prompt: str):
        """Generate & play TTS without blocking the main program."""

        # Unique filename per message
        output_file = os.path.join(self.audio_dir, f"{uuid.uuid4()}.wav")

        # Synthesize audio to file
        with wave.open(output_file, "wb") as wav_file:
            self.voice.synthesize_wav(prompt, wav_file, syn_config=self.syn_config)

        # Play asynchronously (does NOT freeze your program)
        thread = threading.Thread(target=self._play_async, args=(output_file,))
        thread.start()
