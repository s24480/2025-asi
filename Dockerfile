FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    python3-pip git

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements-gradio.txt

WORKDIR /app/src/taxi_fare_prediction/serve_app

EXPOSE ${PORT}

CMD ["python", "gradio_app.py"]
