FROM python:3.10

WORKDIR /app

COPY Dash/ .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8050

CMD ["gunicorn", "app:server", "--bind", "0.0.0.0:8050"]