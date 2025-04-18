FROM python:3.12-bookworm

RUN apt-get update && apt-get install -y

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py", "flights.xml", "--status", "delayed"]