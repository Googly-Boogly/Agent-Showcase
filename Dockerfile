FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Update and install system dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends gcc libpq-dev build-essential \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y ffmpeg

# Install dependencies for visualization
RUN apt-get update \
  && apt-get install -y --no-install-recommends libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /src

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

COPY ./src /src

# Use the startup script as the entry point
CMD ["python3", "main.py"]
