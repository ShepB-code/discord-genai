import os

from dotenv import load_dotenv


def init_environment():
    load_dotenv()

    # required vars
    required_env_vars = ["DISCORD_TOKEN", "GEMINI_TOKEN"]

    for var in required_env_vars:
        if not os.getenv(var):
            raise ValueError(f"{var} not found in environment variables")


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_TOKEN = os.getenv("GEMINI_TOKEN")
