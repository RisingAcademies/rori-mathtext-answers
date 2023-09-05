import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from mathtext.constants import TOKENS2INT_ERROR_INT
from mathtext_fastapi.response_formaters import build_single_event_nlu_response

# Intent recognition model file paths and names
try:
    DATA_DIR = Path(__file__).parent / "data"
    assert DATA_DIR.is_dir()
except NameError:
    DATA_DIR = Path.cwd() / "mathtext" / "data"
except AssertionError:
    try:
        DATA_DIR = Path(__file__).parent.parent / "data"
        assert DATA_DIR.is_dir()
    except AssertionError:
        DATA_DIR = Path.cwd() / "data"

if not DATA_DIR.is_dir():
    DATA_DIR = DATA_DIR.parent
if not DATA_DIR.is_dir():
    DATA_DIR = Path.cwd()  # worst case CWD should always exist
assert DATA_DIR.is_dir()  # without a DATA_DIR this package can't run


# Sentry monitoring link
SENTRY_DSN = os.environ.get("SENTRY_DSN")
SENTRY_TRACES_SAMPLE_RATE = float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE"))
SENTRY_PROFILES_SAMPLE_RATE = float(os.environ.get("SENTRY_PROFILES_SAMPLE_RATE"))

# Supabase logging
SUPABASE_URL = os.environ.get("SUPABASE_URL")

# Cache for NLU Response
REDIS_RESPONSE_CACHE_URL = os.environ.get("REDIS_RESPONSE_CACHE_URL", "")

# Cutoff time for NLU endpoint
TIMEOUT_THRESHOLD = int(os.environ.get("TIMEOUT_THRESHOLD"))
ERROR_RESPONSE_DICT = build_single_event_nlu_response("error", TOKENS2INT_ERROR_INT, 0)
TIMEOUT_RESPONSE_DICT = build_single_event_nlu_response(
    "timeout", TOKENS2INT_ERROR_INT, 0
)

APPROVED_KEYWORDS = ["help", "menu", "stop", "next", "support"]

APPROVED_INTENTS = [
    "change_topic",
    "help",
    "stop",
    "content_question",
    "math_answer",
    "break",
    "safety",
]

APPROVED_INTENT_CONFIDENCE_THRESHOLD = 0.5
