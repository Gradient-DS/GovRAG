FROM python:3.9-slim

WORKDIR /app

# Update pip and system packages
RUN apt-get update && apt-get upgrade -y && pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Assuming your main application is run from app.py
# And that it runs on host 0.0.0.0 to be accessible from other containers
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]