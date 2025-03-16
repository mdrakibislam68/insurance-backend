FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin

WORKDIR /code

COPY requirements.dev.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.dev.txt
COPY . /code/