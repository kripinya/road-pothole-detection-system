#stage1

#1. builder(install dependencies)
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

#stage2 : runtime

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY . .
RUN mkdir -p /app/uploads

EXPOSE 8770

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8770"]

