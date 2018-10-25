#!/bin/bash
set -e

gunicorn --bind=${HOST}:${PORT} app:app
