ARG BUILD_FROM
FROM $BUILD_FROM

# Install system dependencies
RUN apk add --no-cache \
    curl \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt \
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
