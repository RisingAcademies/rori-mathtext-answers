# https://huggingface.co/docs/hub/spaces-sdks-docker-first-demo

# Install / Upgrade Python
FROM python:3.10
RUN python3 -m pip install --no-cache-dir --upgrade poetry pip virtualenv

# Switch into app folder and install dependencies
WORKDIR /code
COPY pyproject.toml ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev
RUN python -m spacy download en_core_web_sm

# Copy application to non-root user's /app folder
COPY . .

# Run server start command
EXPOSE $PORT
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "3"]
