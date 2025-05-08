FROM python:3.9-slim

WORKDIR /app

COPY src/app.py /app/app.py

RUN pip install flask

CMD ["python", "/app/app.py"]