#!/bin/bash

# Quick fix for executable permissions
# Run with: sudo bash fix-permissions.sh

echo "🔧 Fixing executable permissions..."

# Get the correct path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
API_HOME="/opt/azure-test-api"

echo "📁 Script directory: $SCRIPT_DIR"

# Make current directory scripts executable
chmod +x "$SCRIPT_DIR"/*.sh
echo "✅ Made scripts in $SCRIPT_DIR executable"

# If API is installed, fix those too
if [ -d "$API_HOME/deploy" ]; then
    chmod +x "$API_HOME"/deploy/*.sh
    echo "✅ Made scripts in $API_HOME/deploy executable"
fi

echo ""
echo "🎯 Now you can run:"
echo "  sudo ./manage.sh status"
echo "  sudo ./manage.sh start" 
echo "  sudo ./manage.sh logs"
echo ""
echo "Or from anywhere:"
echo "  sudo $API_HOME/deploy/manage.sh status"
echo "  sudo $API_HOME/deploy/manage.sh start"
