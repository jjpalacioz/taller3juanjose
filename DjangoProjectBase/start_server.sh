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

# Try to auto-detect the EC2 public IP from instance metadata.
# If this script is run outside EC2 or the metadata service is unavailable,
# set DJANGO_ALLOWED_HOSTS manually: export DJANGO_ALLOWED_HOSTS="your-ip"
if [ -z "${DJANGO_ALLOWED_HOSTS:-}" ]; then
    _ec2_ip=$(curl -sf --connect-timeout 2 http://169.254.169.254/latest/meta-data/public-ipv4 || true)
    if [ -z "$_ec2_ip" ]; then
        echo "WARNING: Could not auto-detect EC2 public IP. Set DJANGO_ALLOWED_HOSTS manually before running." >&2
        export DJANGO_ALLOWED_HOSTS=""
    else
        export DJANGO_ALLOWED_HOSTS="$_ec2_ip"
    fi
fi
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
# ⚠️  WARNING: Django's runserver is NOT suitable for production.
# It is single-threaded, does not handle concurrent requests well, and
# has not been hardened for exposure to the internet.
# For a real production setup, replace this block with gunicorn:
#   pip install gunicorn
#   gunicorn moviereviews.wsgi:application --bind 0.0.0.0:$DJANGO_PORT --workers 2
echo "==> Starting server on 0.0.0.0:$DJANGO_PORT ..."
echo "    (development server — replace with gunicorn for production)"
python3.11 manage.py runserver 0.0.0.0:"$DJANGO_PORT"
