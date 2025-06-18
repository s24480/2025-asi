FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    python3-pip git

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE ${PORT}

CMD ["python", "app.py"]
