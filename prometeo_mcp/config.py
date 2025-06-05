import os
from dotenv import load_dotenv
from httpx import Timeout
from prometeo import Client

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

PROMETEO_API_KEY = os.environ.get("PROMETEO_API_KEY")
PROMETEO_ENVIRONMENT = os.environ.get("PROMETEO_ENVIRONMENT", "sandbox")
OPENAPI_PATH = "./prometeo_mcp/docs"
HTTPX_TIMEOUT = Timeout(90.0)

if not PROMETEO_API_KEY:
    raise RuntimeError("PROMETEO_API_KEY environment variable is not set")

client = Client(
    api_key=PROMETEO_API_KEY,
    environment=PROMETEO_ENVIRONMENT,
    timeout=HTTPX_TIMEOUT,
)
