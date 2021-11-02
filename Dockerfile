FROM python:3.10 as base
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
COPY . /app
WORKDIR /app
RUN pip install --upgrade pip && pip install -r requirements-dev.txt
