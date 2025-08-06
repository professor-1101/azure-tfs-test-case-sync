#!/bin/bash

# Azure Test Plan Import API - Management Script
# Usage: ./manage.sh {start|stop|restart|status|logs|install|uninstall|update}

SERVICE_NAME="azure-test-api"
API_HOME="/opt/azure-test-api"
API_USER="azureapi"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[AZURE-API]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This operation requires root privileges (use sudo)"
        exit 1
    fi
}

service_start() {
    print_header "Starting Azure Test API service..."
    systemctl start $SERVICE_NAME
    if systemctl is-active --quiet $SERVICE_NAME; then
        print_status "Service started successfully"
        systemctl status $SERVICE_NAME --no-pager -l
    else
        print_error "Failed to start service"
        systemctl status $SERVICE_NAME --no-pager -l
        exit 1
    fi
}

service_stop() {
    print_header "Stopping Azure Test API service..."
    systemctl stop $SERVICE_NAME
    print_status "Service stopped"
}

service_restart() {
    print_header "Restarting Azure Test API service..."
    systemctl restart $SERVICE_NAME
    if systemctl is-active --quiet $SERVICE_NAME; then
        print_status "Service restarted successfully"
    else
        print_error "Failed to restart service"
        exit 1
    fi
}

service_status() {
    print_header "Azure Test API Service Status:"
    systemctl status $SERVICE_NAME --no-pager -l
    
    echo ""
    print_header "Recent logs:"
    journalctl -u $SERVICE_NAME --no-pager -l -n 20
    
    echo ""
    print_header "Service health check:"
    if systemctl is-active --quiet $SERVICE_NAME; then
        echo -e "${GREEN}✓${NC} Service is running"
        # Test API endpoint
        if command -v curl >/dev/null 2>&1; then
            if curl -f -s http://localhost:5050/health >/dev/null; then
                echo -e "${GREEN}✓${NC} API is responding"
            else
                echo -e "${RED}✗${NC} API is not responding"
            fi
        fi
    else
        echo -e "${RED}✗${NC} Service is not running"
    fi
}

service_logs() {
    print_header "Following Azure Test API logs (Ctrl+C to exit):"
    journalctl -u $SERVICE_NAME -f
}

service_install() {
    check_root
    print_header "Installing Azure Test API service..."
    
    # Copy service file
    cp deploy/azure-test-api.service /etc/systemd/system/
    
    # Reload systemd
    systemctl daemon-reload
    
    # Enable service
    systemctl enable $SERVICE_NAME
    
    print_status "Service installed and enabled"
    print_status "Use './manage.sh start' to start the service"
}

service_uninstall() {
    check_root
    print_header "Uninstalling Azure Test API service..."
    
    # Stop service
    systemctl stop $SERVICE_NAME 2>/dev/null || true
    
    # Disable service
    systemctl disable $SERVICE_NAME 2>/dev/null || true
    
    # Remove service file
    rm -f /etc/systemd/system/$SERVICE_NAME.service
    
    # Reload systemd
    systemctl daemon-reload
    
    print_status "Service uninstalled"
    print_warning "Application files in $API_HOME are preserved"
}

service_update() {
    check_root
    print_header "Updating Azure Test API..."
    
    # Stop service
    print_status "Stopping service..."
    systemctl stop $SERVICE_NAME
    
    # Backup current installation
    print_status "Creating backup..."
    tar -czf /tmp/azure-api-backup-$(date +%Y%m%d-%H%M%S).tar.gz -C $API_HOME .
    
    # Update code (assuming git repository)
    print_status "Updating application code..."
    if [ -d "$API_HOME/.git" ]; then
        sudo -u $API_USER git -C $API_HOME pull origin main
    else
        print_warning "Not a git repository. Please manually update the code."
    fi
    
    # Update dependencies
    print_status "Updating Python dependencies..."
    sudo -u $API_USER $API_HOME/venv/bin/pip install --upgrade pip
    sudo -u $API_USER $API_HOME/venv/bin/pip install -r $API_HOME/requirements.txt
    
    # Restart service
    print_status "Starting service..."
    systemctl start $SERVICE_NAME
    
    if systemctl is-active --quiet $SERVICE_NAME; then
        print_status "Update completed successfully"
    else
        print_error "Update failed. Check logs for details."
        exit 1
    fi
}

show_help() {
    echo "Azure Test Plan Import API - Management Script"
    echo ""
    echo "Usage: $0 {command}"
    echo ""
    echo "Commands:"
    echo "  start      Start the API service"
    echo "  stop       Stop the API service"  
    echo "  restart    Restart the API service"
    echo "  status     Show service status and health"
    echo "  logs       Follow service logs"
    echo "  install    Install systemd service (requires sudo)"
    echo "  uninstall  Remove systemd service (requires sudo)"
    echo "  update     Update application and restart (requires sudo)"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 status"
    echo "  sudo $0 install"
    echo "  sudo $0 update"
}

# Main script logic
case "${1:-}" in
    start)
        check_root
        service_start
        ;;
    stop)
        check_root
        service_stop
        ;;
    restart)
        check_root
        service_restart
        ;;
    status)
        service_status
        ;;
    logs)
        service_logs
        ;;
    install)
        service_install
        ;;
    uninstall)
        service_uninstall
        ;;
    update)
        service_update
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: ${1:-}"
        echo ""
        show_help
        exit 1
        ;;
esac
