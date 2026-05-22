FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY run.py /app/run.py

ENTRYPOINT ["python", "/app/run.py"]
CMD ["--input", "/data/images", "--output", "/data/results.json"]
