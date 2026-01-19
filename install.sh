#!/bin/bash
#
# Home AI Assistant - Quick Install Script
# 
# Usage: curl -fsSL https://raw.githubusercontent.com/TaraHome/TaraAssistant/main/install.sh | bash
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════╗"
echo "║         Tara Assistant Installer          ║"
echo "╚═══════════════════════════════════════════╝"
echo -e "${NC}"

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed.${NC}"
    echo ""
    echo "Please install Docker first:"
    echo "  - Mac: https://docs.docker.com/desktop/install/mac-install/"
    echo "  - Windows: https://docs.docker.com/desktop/install/windows-install/"
    echo "  - Linux: https://docs.docker.com/engine/install/"
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker found"

# Check for Docker Compose
if ! docker compose version &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not available.${NC}"
    echo "Please make sure Docker Desktop is running."
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker Compose found"

# Create installation directory
INSTALL_DIR="$HOME/tara-assistant"
echo ""
echo -e "${BLUE}Installing to: ${INSTALL_DIR}${NC}"

mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Create data directory for encrypted credentials with correct permissions
mkdir -p data
# Set ownership to match container user (UID 1000)
if command -v sudo &> /dev/null; then
    sudo chown -R 1000:1000 data 2>/dev/null || chmod 777 data
else
    chmod 777 data
fi

# Download docker-compose.yml
echo -e "${YELLOW}Downloading configuration...${NC}"
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  tara-assistant:
    image: ghcr.io/tarahome/taraassistant:latest
    container_name: tara-assistant
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - TZ=America/New_York
EOF

echo -e "${GREEN}✓${NC} Configuration created"

# Pull the image
echo ""
echo -e "${YELLOW}Pulling Docker image (this may take a minute)...${NC}"
docker compose pull 2>/dev/null || {
    echo -e "${YELLOW}Image not found in registry. Building locally...${NC}"
    # If no pre-built image, clone and build
    if [ ! -f "Dockerfile" ]; then
        echo -e "${YELLOW}Cloning repository...${NC}"
        git clone https://github.com/TaraHome/TaraAssistant.git temp
        mv temp/* .
        mv temp/.* . 2>/dev/null || true
        rm -rf temp
    fi
    docker compose build
}

# Start the container
echo ""
echo -e "${YELLOW}Starting Tara Assistant...${NC}"
docker compose up -d

# Wait for startup
echo -e "${YELLOW}Waiting for service to start...${NC}"
sleep 5

# Check if running
if docker compose ps | grep -q "running"; then
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║     Installation Complete! 🎉              ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "Open your browser to: ${BLUE}http://localhost:8000${NC}"
    echo ""
    echo "You'll be guided through setup to connect:"
    echo "  • Your Home Assistant instance"
    echo "  • Your AI provider (OpenAI, Anthropic, or local Ollama)"
    echo ""
    echo -e "${YELLOW}All credentials are encrypted locally on your machine.${NC}"
    echo ""
    echo "Useful commands:"
    echo "  cd $INSTALL_DIR"
    echo "  docker compose logs -f    # View logs"
    echo "  docker compose restart    # Restart"
    echo "  docker compose down       # Stop"
    echo ""
else
    echo -e "${RED}Error: Failed to start. Check logs with: docker compose logs${NC}"
    exit 1
fi
