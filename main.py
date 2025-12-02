import asyncio
import time
import yaml
from avatar import vmc_client
from voice import tts
from utils import logger


# Load config
with open("config/settings.yaml", "r", encoding="utf-8") as f:
    SETTINGS = yaml.safe_load(f)


async def main():
    # Initialize VMC client
    vmc = vmc_client.VMCClient(
        host=SETTINGS.get("vmc_host", "127.0.0.1"),
        port=SETTINGS.get("vmc_port", 39539)
    )

    # Initialize TTS engine
    tts_engine = tts.TextToSpeech()

    # Test speech
    tts_engine.Speech("Hello, World")

    # Keep the async loop alive (for networking / vmc updates)
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
