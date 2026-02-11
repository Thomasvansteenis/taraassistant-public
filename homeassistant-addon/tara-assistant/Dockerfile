ARG BUILD_FROM
FROM $BUILD_FROM

# Install Python and system dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    python3-dev \
    curl \
    jq \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# Copy application code
COPY app/ ./app/
COPY scripts.yaml ./scripts.yaml

# Copy entrypoint
COPY run.sh /run.sh
RUN chmod a+x /run.sh

# Create data directory
RUN mkdir -p /data/app_data

CMD ["/run.sh"]
