FROM python:3.10-slim

# Install uv, a fast python package installer
RUN pip install uv

WORKDIR /app


# Copy requirements.txt
COPY requirements.txt ./

# Install dependencies using uv pip (system-wide)
RUN uv pip install --system -r requirements.txt

# Copy the rest of the application code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]