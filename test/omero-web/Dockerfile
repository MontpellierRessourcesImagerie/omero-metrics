FROM ghcr.io/manics/omero-web-docker:ubuntu
USER root

# Install system dependencies and Node.js 20 LTS
RUN apt-get update && \
    apt-get install -y --no-install-recommends git curl ca-certificates gnupg && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
        | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" \
        > /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN /opt/omero/web/venv3/bin/pip install --no-cache-dir -r ./requirements.txt

# Install React
ENV REACT_VERSION=18.2.0
RUN npm install react@${REACT_VERSION}

# Copy startup script
COPY ./98-dash-migrate.sh /startup/
RUN chmod +x /startup/98-dash-migrate.sh

USER omero-web
