import os
from pathlib import Path
# from supabase import create_client

from dotenv import load_dotenv
load_dotenv()

# Intent recognition model file paths and names
try:
    DATA_DIR = Path(__file__).parent / 'data'
    assert DATA_DIR.is_dir()
except NameError:
    DATA_DIR = Path.cwd() / 'mathtext' / 'data'  
except AssertionError:
    try:
        DATA_DIR = Path(__file__).parent.parent / 'data'
        assert DATA_DIR.is_dir()
    except AssertionError:
        DATA_DIR = Path.cwd() / 'data'

if not DATA_DIR.is_dir():
    DATA_DIR = DATA_DIR.parent
if not DATA_DIR.is_dir():
    DATA_DIR = Path.cwd()  # worst case CWD should always exist
assert DATA_DIR.is_dir()  # without a DATA_DIR this package can't run

DEFAULT_MODEL_FILENAME = "intent_classification_model.joblib"
DEFAULT_LABELED_DATA = "labeled_data.csv"

MODEL_PATH = DATA_DIR / DEFAULT_MODEL_FILENAME
LABELED_DATA_PATH = DATA_DIR / DEFAULT_LABELED_DATA

# Sentry monitoring link
SENTRY_DSN = os.environ.get('SENTRY_DSN')

# Supabase logging via sdk
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
SUPABASE_LINK = os.environ.get('SUPABASE_LINK')
# SUPA = create_client(
#     SUPABASE_URL,
#     SUPABASE_KEY
# )
