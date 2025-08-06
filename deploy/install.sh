#!/bin/bash

# Azure Test Plan Import API - Installation Script
# Run with: sudo bash install.sh

set -e

echo "🚀 Installing Azure Test Plan Import API..."

# Configuration
API_USER="azureapi"
API_HOME="/opt/azure-test-api"
SERVICE_NAME="azure-test-api"
PYTHON_VERSION="3.9"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

print_status "Updating system packages..."
apt update && apt upgrade -y

print_status "Installing system dependencies..."
apt install -y python3 python3-pip python3-venv nginx supervisor git curl

# Create dedicated user
print_status "Creating dedicated user: $API_USER"
if ! id "$API_USER" &>/dev/null; then
    useradd --system --shell /bin/bash --home-dir $API_HOME --create-home $API_USER
    print_status "User $API_USER created"
else
    print_warning "User $API_USER already exists"
fi

# Create application directory
print_status "Setting up application directory..."
mkdir -p $API_HOME
chown $API_USER:$API_USER $API_HOME

# Clone or copy application
print_status "Setting up application files..."
if [ -d "/tmp/azure-test-api" ]; then
    cp -r /tmp/azure-test-api/* $API_HOME/
else
    # If running from current directory
    cp -r . $API_HOME/
fi

# Set correct permissions
chown -R $API_USER:$API_USER $API_HOME
chmod +x $API_HOME/deploy/*.sh

print_status "Creating Python virtual environment..."
sudo -u $API_USER python3 -m venv $API_HOME/venv

print_status "Installing Python dependencies..."
sudo -u $API_USER $API_HOME/venv/bin/pip install --upgrade pip
sudo -u $API_USER $API_HOME/venv/bin/pip install -r $API_HOME/requirements.txt
sudo -u $API_USER $API_HOME/venv/bin/pip install gunicorn uvloop

# Create logs directory
print_status "Setting up logging..."
mkdir -p $API_HOME/logs
chown $API_USER:$API_USER $API_HOME/logs

# Create environment file
print_status "Creating environment configuration..."
cat > $API_HOME/.env << EOF
# Azure DevOps Configuration
AZURE_DEVOPS_ORG_URL=http://your-server:8080/tfs/YourCollection
AZURE_DEVOPS_PROJECT_NAME=YourProject
AZURE_DEVOPS_USERNAME=YourUsername
AZURE_DEVOPS_PASSWORD=YourPassword

# API Configuration  
API_HOST=0.0.0.0
API_PORT=5050
LOG_LEVEL=INFO

# Auto-detect server IP for display
SERVER_IP=$(hostname -I | awk '{print $1}' || echo "127.0.0.1")

# Security (generate new secret key)
SECRET_KEY=$(openssl rand -hex 32)

# Performance
WORKERS=4
EOF

chown $API_USER:$API_USER $API_HOME/.env
chmod 600 $API_HOME/.env

print_status "Installation completed!"
print_warning "Please edit $API_HOME/.env with your Azure DevOps credentials"

# Detect and display server IP
SERVER_IP=$(hostname -I | awk '{print $1}' || echo "127.0.0.1")

print_status "Server will be available at: http://$SERVER_IP:5050"
print_status "Next steps:"
echo "  1. Edit configuration: sudo nano $API_HOME/.env"
echo "  2. Start service: sudo systemctl start $SERVICE_NAME"
echo "  3. Enable autostart: sudo systemctl enable $SERVICE_NAME" 
echo "  4. Check status: sudo systemctl status $SERVICE_NAME"
echo "  5. View logs: sudo journalctl -u $SERVICE_NAME -f"
echo ""
print_status "After starting the service, access:"
echo "  📡 API: http://$SERVER_IP:5050"
echo "  📖 Docs: http://$SERVER_IP:5050/docs"
echo "  🔍 Health: http://$SERVER_IP:5050/health"
