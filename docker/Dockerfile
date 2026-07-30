# Build
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime
FROM python:3.11-slim
WORKDIR /app

RUN useradd -m appuser

COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local
COPY --chown=appuser:appuser app/ .

ENV PATH=/home/appuser/.local/bin:$PATH

USER appuser

CMD ["python", "main.py"]