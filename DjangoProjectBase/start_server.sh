#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# start_server.sh — Start the Django movie-reviews app on an EC2 instance.
#
# Usage:
#   chmod +x start_server.sh
#   ./start_server.sh
#
# Environment variables you can override before running:
#   DJANGO_DEBUG          — "False" for production (default: False)
#   DJANGO_ALLOWED_HOSTS  — comma-separated public IPs / hostnames
#   DJANGO_PORT           — TCP port to listen on (default: 8000)
#   OPENAI_ENV_FILE       — path to the openAI.env file
# ---------------------------------------------------------------------------

set -euo pipefail

# ---------- configuration (edit or export these before running) ----------
export DJANGO_DEBUG="${DJANGO_DEBUG:-False}"
export DJANGO_ALLOWED_HOSTS="${DJANGO_ALLOWED_HOSTS:-$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)}"
DJANGO_PORT="${DJANGO_PORT:-8000}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Working directory: $SCRIPT_DIR"
echo "==> DEBUG            : $DJANGO_DEBUG"
echo "==> ALLOWED_HOSTS    : $DJANGO_ALLOWED_HOSTS"
echo "==> Port             : $DJANGO_PORT"

cd "$SCRIPT_DIR"

# ---------- apply migrations ----------
echo "==> Running migrations..."
python3.11 manage.py migrate --noinput

# ---------- collect static files ----------
echo "==> Collecting static files..."
python3.11 manage.py collectstatic --noinput

# ---------- start the development server ----------
# For a real production setup replace this with gunicorn:
#   gunicorn moviereviews.wsgi:application --bind 0.0.0.0:$DJANGO_PORT
echo "==> Starting server on 0.0.0.0:$DJANGO_PORT ..."
python3.11 manage.py runserver 0.0.0.0:"$DJANGO_PORT"
