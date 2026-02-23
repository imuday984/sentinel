FROM python:3.10-slim
WORKDIR /app
# We need numpy and redis
RUN pip install --no-cache-dir redis numpy
COPY . .
CMD ["python", "consumer.py"]