FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    g++ \
    gcc \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libx264-dev \
    make \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip setuptools wheel

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /backend

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

CMD ["sh", "-c", "python /backend/migrations/init_db.py && python /backend/run.py"]
