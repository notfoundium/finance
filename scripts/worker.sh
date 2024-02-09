#!/usr/bin/env bash

celery -A worker.tasks:queue worker --loglevel=ERROR -B
