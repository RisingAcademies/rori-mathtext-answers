import os
from pathlib import Path

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


# Sentry monitoring link
SENTRY_DSN = os.environ.get('SENTRY_DSN')
SENTRY_TRACES_SAMPLE_RATE = os.environ.get('SENTRY_TRACES_SAMPLE_RATE')

# Supabase logging via sdk
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
SUPABASE_LINK = os.environ.get('SUPABASE_LINK')

PROD_SUPABASE_DB = os.environ.get('PROD_SUPABASE_DB')
PROD_SUPABASE_DBNAME = os.environ.get('PROD_SUPABASE_DBNAME')
PROD_SUPABASE_USER = os.environ.get('PROD_SUPABASE_USER')
PROD_SUPABASE_PW = os.environ.get('PROD_SUPABASE_PW')

# Cache for NLU Response
REDIS_RESPONSE_CACHE_URL = os.environ.get('REDIS_RESPONSE_CACHE_URL')