FROM python:3.13-slim

WORKDIR /app

# Install system tools and Node.js (with npm and npx)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    ca-certificates \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install uv globally
RUN pip install --upgrade pip && pip install uv

# Copy project files including pyproject.toml and uv.lock (if exists)
COPY . .

# Create virtual environment and sync dependencies
RUN uv venv && uv pip install --upgrade pip && uv sync --no-dev

EXPOSE 8081

# Run FastAPI app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]
