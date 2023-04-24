import os
from pathlib import Path
from supabase import create_client

from dotenv import load_dotenv
load_dotenv()

# Intent recognition model file paths and names
DATA_DIR = Path(__file__).parent.parent / "mathtext_fastapi" / "data"

DEFAULT_MODEL_FILENAME = "intent_classification_model.joblib"
DEFAULT_LABELED_DATA = "labeled_data.csv"

MODEL_PATH = DATA_DIR / DEFAULT_MODEL_FILENAME
LABELED_DATA_PATH = DATA_DIR / DEFAULT_LABELED_DATA

# Sentry monitoring link
SENTRY_DSN = os.environ.get('SENTRY_DSN')

# Supabase logging via sdk
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
SUPA = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)
