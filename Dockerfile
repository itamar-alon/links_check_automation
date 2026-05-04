FROM python:3.9-slim

RUN apt-get update && apt-get install -y google-chrome-stable

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD ["pytest", "tests/test_full_flow.py"]