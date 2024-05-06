FROM python:3.7-alpine

RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev

ENV PYTHONUNBUFFERED 1
RUN mkdir /code

#define work dir
WORKDIR /code
COPY requirements.txt /code/

# install packages in requirements
RUN python -m pip install -r requirements.txt

COPY . /code