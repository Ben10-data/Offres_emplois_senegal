FROM python:3.10

WORKDIR /app

COPY Fastapi/ .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]FROM python:3.10

WORKDIR /app

COPY Fastapi/ /app/app

COPY zenML/src /app/src



RUN pip install --no-cache-dir -r /app/app/requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]