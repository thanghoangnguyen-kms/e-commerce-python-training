FROM python:3.11-slim

# Install uv
RUN pip install --upgrade pip && pip install uv

WORKDIR /app

# Copy metadata first (cacheable layer)
COPY pyproject.toml ./
# If you have uv.lock, copy it too to make builds reproducible:
# COPY uv.lock ./

# Create a project venv and install only runtime deps
RUN uv sync --no-dev

# Activate .venv for all subsequent RUN/CMD
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy source
COPY app ./app

# Run the app (no need to prefix with `uv run` now)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
