FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY run_all.py .

# Output directory for scraped data, to be mounted as a volume
VOLUME /app/data

CMD ["python", "run_all.py"] 