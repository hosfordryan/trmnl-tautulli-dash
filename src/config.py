import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Config for the project
class Config:
    HOST_IP = os.getenv("HOST_IP", "0.0.0.0")
    HOST_PORT = int(os.getenv("HOST_PORT", 3113))

    TAUTULLI_IP = os.getenv("TAUTULLI_IP", "0.0.0.0")
    TAUTULLI_PORT = os.getenv("PORT", "8181")
    TAUTULLI_API_KEY = os.getenv("TAUTULLI_API_KEY")

    # Plugin config
    REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", 900))
    CACHE_TIMEOUT_SEC = 3600  # 1 hour

    # TRMNL config
    TRMNL_API_KEY = os.getenv("TRMNL_API_KEY")
    TRMNL_PLUGIN_UUID = os.getenv("TRMNL_PLUGIN_UUID")

    @classmethod
    def validate(cls):
        # Validate required config
        required_keys = ["TRMNL_API_KEY", "TRMNL_PLUGIN_UUID", "TAUTULLI_API_KEY"]

        missing_keys = [key for key in required_keys if not getattr(cls, key)]
        if missing_keys:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing_keys)}"
            )
