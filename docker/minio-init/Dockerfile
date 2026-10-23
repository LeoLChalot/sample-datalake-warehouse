FROM python:3.11-alpine

RUN pip install --no-cache-dir boto3

WORKDIR /app
COPY init_buckets.py .

CMD ["python", "init_buckets.py"]
