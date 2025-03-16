FROM python:3.9

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

COPY entrypoint.dev.sh /
ENTRYPOINT ["sh", "./entrypoint.dev.sh"]