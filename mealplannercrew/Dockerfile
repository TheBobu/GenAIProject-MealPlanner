FROM python:3.11-slim

WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ./

COPY requirements.txt ./

RUN pip install -r requirements.txt

# Install dependencies using uv
RUN uv sync --frozen

# Copy application code
COPY . .

# Create knowledge directory for database
RUN mkdir -p knowledge

# Expose port
EXPOSE 8000

# Run the application using uv
CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]