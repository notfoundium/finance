FROM python:3.10.12-slim-buster

USER root

RUN apt-get update && \
    apt clean && \
    rm -rf /var/cache/apt/*

COPY requirements/ /tmp/requirements

RUN pip install -U pip && \
    pip install --no-cache-dir -r /tmp/requirements/base.txt

COPY . /src
ENV PATH "$PATH:/src/scripts"

WORKDIR /src
