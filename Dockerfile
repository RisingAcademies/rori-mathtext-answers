# https://huggingface.co/docs/hub/spaces-sdks-docker-first-demo

# Install / Upgrade Python
FROM python:3.10
RUN python3 -m pip install --no-cache-dir --upgrade poetry pip virtualenv

# Switch into app folder and install dependencies
WORKDIR /code
# RUN python3 -m virtualenv .venv
# ENV PATH="/mathtext-fastapi/venv/bin:$PATH"
COPY pyproject.toml ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev

# Install and switch to a non-root user
# RUN useradd -m -u 1000 user
# USER user
# ENV HOME=/home/user \
#         PATH=/home/user/.local/bin:$PATH

# Copy application to non-root user's /app folder
# WORKDIR $HOME/app
# COPY --chown=user . $HOME/app
COPY . .

# Run server start command
EXPOSE $PORT
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "3"]
