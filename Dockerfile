FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY * *

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

CMD ["sh", "-c", "python /migrations/init_db.py && python /run.py"]
