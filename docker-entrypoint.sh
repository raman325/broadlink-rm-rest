#!/bin/bash
set -e

gunicorn --bind=${HOST}:${PORT} broadlink_rm_rest_app:app
