FROM python:3.11-slim

WORKDIR /app
COPY mqtt_to_postgres.py .

# Install dependencies
RUN pip install --no-cache-dir paho-mqtt psycopg2-binary

# Unbuffered output for docker logs
ENV PYTHONUNBUFFERED=1

CMD ["python", "mqtt_to_postgres.py"]