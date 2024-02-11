FROM python:3.10.12-slim-buster

USER root

RUN apt-get update && \
    apt clean && \
    rm -rf /var/cache/apt/*

COPY . /src
ENV PATH "$PATH:/src/scripts"

WORKDIR /src

RUN pip install -U pip poetry && \
    poetry install
