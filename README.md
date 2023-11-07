# Math Answers API
### Project Overview
The Math Answers API provides a service to support a math chatbot in understanding the content of a student message.  The API offers endpoints with combinations of text processing and intent recognition to evaluate messages.

This repository focuses on the API service.
The [mathtext repository](https://gitlab.com/tangibleai/community/mathtext/-/tree/main) focused on the NLU text processing and intent recognition service.  This is [uploaded to PyPi](https://pypi.org/project/mathtext/) and is a dependency of the Math Answers API.


### Local Development Setup
The Math Answers API uses Python 3.10.  
```
# 1. Clone the repository
git clone https://github.com/RisingAcademies/rori-mathtext-answers

# 2. Move into Math Answers API
cd rori-mathtext-answers

# 3. Install build environment tools
pip install --upgrade virtualenv

# 4. Create a virtual environment
python -m virutalenv .venv

# 5. Activate the virtual environment (Linux || Windows)
source .venv/bin/activate || source .venv/scripts/activate

# 6. Install Math Answers API dependencies
pip install --editable .
```


### Run locally
`uvicorn app:app --host localhost --port 7860`


### Test locally
`pytest`


### Directory Structure
```bash
|-- mathtext_fastapi
| |-- data
| |-- nlu_evaluations
| | |-- evaluation_utils.py # Support functions for message evaluations
| | |-- evaluations.py # Evaluations for specific types of responses
| |-- cache.py
| |-- constants.py # Configuration variables for the application
| |-- request_validators.py # Validates the request object
| |-- response_formaters.py # Converts evaluation result to response obj
| |-- supabase_logging_async.py # Background logging Deque management
| |-- v2_nlu.py # Sequences of evaluations
|-- scripts
|-- tests
|-- CHANGELOG.md
|-- pyproject.toml
|-- Dockerfile
|-- app.py # Main FastAPI application and endpoints
```
