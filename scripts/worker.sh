#!/usr/bin/env bash

poetry run celery -A worker.tasks:queue worker --loglevel=ERROR -B
