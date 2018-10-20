#!/bin/bash
set -e

gunicorn --bind=${HOST}:${PORT} rest_app:app
