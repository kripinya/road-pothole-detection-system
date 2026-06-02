# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .


#install pytorch cpu-only first
RUN pip install --no-cache-dir --user \
    torch==2.5.0+cpu \
    torchvision==0.20.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local

COPY . .

RUN mkdir -p /app/models /app/data

EXPOSE 8771

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8771"]