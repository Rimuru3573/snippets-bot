FROM python:3.11-slim

WORKDIR /app

COPY bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot/ .

COPY utils/ ./utils/

ENV PYTHONPATH=/app

CMD ["python", "main.py"]