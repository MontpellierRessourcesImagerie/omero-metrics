set -eu

export PATH="/opt/omero/web/venv3/bin:$PATH"
python=/opt/omero/web/venv3/bin/python

# Clear stale .pyc files from bind-mounted code (local Python version may differ)
echo "Clearing stale __pycache__ from omero_metrics"
find /opt/omero/web/venv3/lib/python3.10/site-packages/omero_metrics \
    -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

cd /opt/omero/web/venv3/lib/python3.10/site-packages/omeroweb

echo "Run migrate to update the database OMERO.web"
$python manage.py migrate

echo "Collecting static files for OMERO.web"
$python manage.py collectstatic --noinput