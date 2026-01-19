#
# Home AI Assistant - Windows Install Script
#
# Usage: Run in PowerShell as Administrator
# irm https://raw.githubusercontent.com/TaraHome/TaraAssistant/main/install.ps1 | iex
#

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔═══════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║         Tara Assistant Installer          ║" -ForegroundColor Blue
Write-Host "╚═══════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""

# Check for Docker
try {
    docker --version | Out-Null
    Write-Host "✓ Docker found" -ForegroundColor Green
} catch {
    Write-Host "Error: Docker is not installed." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Docker Desktop first:"
    Write-Host "https://docs.docker.com/desktop/install/windows-install/"
    exit 1
}

# Check Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "Error: Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

Write-Host "✓ Docker is running" -ForegroundColor Green

# Create installation directory
$InstallDir = "$env:USERPROFILE\tara-assistant"
Write-Host ""
Write-Host "Installing to: $InstallDir" -ForegroundColor Blue

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
New-Item -ItemType Directory -Force -Path "$InstallDir\data" | Out-Null
Set-Location $InstallDir

# Create docker-compose.yml
Write-Host "Downloading configuration..." -ForegroundColor Yellow

$ComposeContent = @"
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
"@

$ComposeContent | Out-File -FilePath "docker-compose.yml" -Encoding UTF8
Write-Host "✓ Configuration created" -ForegroundColor Green

# Pull and start
Write-Host ""
Write-Host "Pulling Docker image (this may take a minute)..." -ForegroundColor Yellow

try {
    docker compose pull
} catch {
    Write-Host "Image not found. Building locally..." -ForegroundColor Yellow
    git clone https://github.com/TaraHome/TaraAssistant.git temp
    Copy-Item -Path "temp\*" -Destination "." -Recurse -Force
    Remove-Item -Path "temp" -Recurse -Force
    docker compose build
}

Write-Host ""
Write-Host "Starting Tara Assistant..." -ForegroundColor Yellow
docker compose up -d

Start-Sleep -Seconds 5

# Check if running
$status = docker compose ps --format json | ConvertFrom-Json
if ($status.State -eq "running") {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║     Installation Complete! 🎉              ║" -ForegroundColor Green  
    Write-Host "╚═══════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "Open your browser to: " -NoNewline
    Write-Host "http://localhost:8000" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You'll be guided through setup to connect:"
    Write-Host "  • Your Home Assistant instance"
    Write-Host "  • Your AI provider (OpenAI, Anthropic, or local Ollama)"
    Write-Host ""
    Write-Host "All credentials are encrypted locally on your machine." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Useful commands:"
    Write-Host "  cd $InstallDir"
    Write-Host "  docker compose logs -f    # View logs"
    Write-Host "  docker compose restart    # Restart"
    Write-Host "  docker compose down       # Stop"
} else {
    Write-Host "Error: Failed to start. Check logs with: docker compose logs" -ForegroundColor Red
    exit 1
}
