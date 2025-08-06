#!/bin/bash

# Azure Test API Health Check Script
# Can be used with cron for monitoring

# Auto-detect server IP or use localhost as fallback
SERVER_IP=$(hostname -I | awk '{print $1}' || echo "127.0.0.1")
API_URL="http://$SERVER_IP:5050"
SERVICE_NAME="azure-test-api"
LOG_FILE="/var/log/azure-api-health.log"
MAX_LOG_SIZE=10485760  # 10MB

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Logging function
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Rotate log if too large
rotate_log() {
    if [ -f "$LOG_FILE" ] && [ $(stat -c%s "$LOG_FILE") -gt $MAX_LOG_SIZE ]; then
        mv "$LOG_FILE" "${LOG_FILE}.old"
        touch "$LOG_FILE"
    fi
}

# Check if service is running
check_service() {
    if systemctl is-active --quiet $SERVICE_NAME; then
        return 0
    else
        return 1
    fi
}

# Check API health endpoint
check_api_health() {
    local response
    local http_code
    
    if command -v curl >/dev/null 2>&1; then
        response=$(curl -s -w "%{http_code}" -o /dev/null --connect-timeout 10 --max-time 30 "$API_URL/health")
        http_code=$response
        
        if [ "$http_code" = "200" ]; then
            return 0
        else
            log_message "ERROR: API health check failed (HTTP $http_code)"
            return 1
        fi
    else
        log_message "WARNING: curl not available for health check"
        return 1
    fi
}

# Check API functionality with test request
check_api_functionality() {
    local response
    local http_code
    
    response=$(curl -s -w "%{http_code}" -o /dev/null --connect-timeout 10 --max-time 30 "$API_URL/api/v1/test-plans")
    http_code=$response
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "401" ]; then
        # 200 = OK, 401 = Authentication required (expected)
        return 0
    else
        log_message "ERROR: API functionality check failed (HTTP $http_code)"
        return 1
    fi
}

# Check disk space
check_disk_space() {
    local usage
    usage=$(df /opt/azure-test-api | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$usage" -gt 90 ]; then
        log_message "WARNING: Disk usage is ${usage}% on /opt/azure-test-api"
        return 1
    elif [ "$usage" -gt 80 ]; then
        log_message "INFO: Disk usage is ${usage}% on /opt/azure-test-api"
    fi
    
    return 0
}

# Check memory usage
check_memory() {
    local pid
    local memory_mb
    
    pid=$(pgrep -f "gunicorn.*main:app")
    if [ -n "$pid" ]; then
        memory_mb=$(ps -p $pid -o rss= | awk '{print int($1/1024)}')
        
        if [ "$memory_mb" -gt 1000 ]; then
            log_message "WARNING: High memory usage: ${memory_mb}MB"
            return 1
        fi
    fi
    
    return 0
}

# Restart service if needed
restart_service() {
    log_message "RESTARTING: Azure Test API service"
    
    # Check if service is enabled for auto-start
    if ! systemctl is-enabled --quiet $SERVICE_NAME; then
        log_message "WARNING: Service is not enabled for auto-start"
        log_message "ENABLING: Service for auto-start on boot"
        systemctl enable $SERVICE_NAME
    fi
    
    systemctl restart $SERVICE_NAME
    
    # Wait for service to start
    sleep 10
    
    if check_service && check_api_health; then
        log_message "SUCCESS: Service restarted successfully"
        return 0
    else
        log_message "ERROR: Service restart failed"
        return 1
    fi
}

# Main health check
main() {
    rotate_log
    
    local service_ok=true
    local api_ok=true
    local disk_ok=true
    local memory_ok=true
    
    # Check service status
    if ! check_service; then
        log_message "ERROR: Service $SERVICE_NAME is not running"
        service_ok=false
    fi
    
    # Check API health
    if ! check_api_health; then
        api_ok=false
    fi
    
    # Check API functionality
    if ! check_api_functionality; then
        api_ok=false
    fi
    
    # Check resources
    if ! check_disk_space; then
        disk_ok=false
    fi
    
    if ! check_memory; then
        memory_ok=false
    fi
    
    # Decide on action
    if [ "$service_ok" = false ] || [ "$api_ok" = false ]; then
        if [ "$1" = "--auto-restart" ]; then
            restart_service
        else
            log_message "ALERT: Service requires attention (use --auto-restart for automatic restart)"
            exit 1
        fi
    else
        if [ "$1" = "--verbose" ]; then
            log_message "OK: All health checks passed"
        fi
    fi
}

# Show usage
show_usage() {
    clear
    echo "                                                                                                    "
    echo "                            ███████████████████████████████████████████                             "
    echo "                          ███████████████████████████████████████████████                           "
    echo "                        ███████████████████████████████████████████████████                         "
    echo "                      ███████████████████████████████████████████████████████                       "
    echo "                    ███████████████████████████████████████████████████████████                     "
    echo "                  ███████████████████████████████████████████████████████████████                   "
    echo "                 ██████████████████████████████████████████████████████████████████                 "
    echo "               ██████████████████████████████████████████████████████████████████████               "
    echo "             █████████████████████████████████████████████████████████████████████████              "
    echo "           █████████████████████████████████████████████████████████████████████████████            "
    echo "         █████████████████████████████████████████████████████████████████████████████████          "
    echo "        ███████████████████████████████████████████████████████████████████████████████████         "
    echo "       █████████████████████████████████████████████████████████████████████████████████████        "
    echo "       ██████████████████████████                                  █████████████████████████        "
    echo "       ████████████████████████                                      ███████████████████████        "
    echo "       ██████████████████████                                         ██████████████████████        "
    echo "       ██████████████████████                                         ██████████████████████        "
    echo "       ██████████████████████                                         ██████████████████████        "
    echo "       ██████████████████████                                         ██████████████████████        "
    echo "       ██████████████████████                                         ██████████████████████        "
    echo "       ██████████████████████                                         ██████████████████████        "
    echo "       ██████████████████████                                         ██████████████████████        "
    echo "       ██████████████████████                                         ██████████████████████        "
    echo "       ██████████████████████                                         ██████████████████████        "
    echo "       ██████████████████████                      █████████████████████████████████████████        "
    echo "       ██████████████████████                    ████████████████████████                           "
    echo "       ██████████████████████                    ██████████████████████████                         "
    echo "       ██████████████████████                    ████████████████████████████                       "
    echo "       ██████████████████████                    ██████████████████████████████                     "
    echo "       ██████████████████████                    ████████████████████████████████                   "
    echo "       ██████████████████████                    █████████████████████████████████                  "
    echo "       ██████████████████████                    ███████████████████████████████████                "
    echo "       ██████████████████████                    █████████████████████████████████████              "
    echo "       ██████████████████████                    ███████████████████████████████████████            "
    echo "       ███████████████████████                   █████████████████████████████████████████          "
    echo "       █████████████████████████                 ██████████████████████████████████████████         "
    echo "       ██████████████████████████████████████████████████████████████████████████████████████       "
    echo "        ███████████████████████████████████████████████████████████████                             "
    echo "         █████████████████████████████████████████ ████████████████████                             "
    echo "           ███████████████████████████████████████   ██████████████████                             "
    echo "            ██████████████████████████████████████     ████████████████                             "
    echo "              ████████████████████████████████████       ██████████████                             "
    echo "                ██████████████████████████████████         ████████████                             "
    echo "                  ████████████████████████████████          ███████████                             "
    echo "                    ██████████████████████████████            █████████                             "
    echo "                      ████████████████████████████              ███████                             "
    echo "                       ███████████████████████████                █████                             "
    echo "                         █████████████████████████                  ███                             "
    echo "                           ███████████████████████                    █                             "
    echo "                                                                                                    "
    echo ""
    echo "Azure Test API Health Check"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --auto-restart    Automatically restart service if unhealthy"
    echo "  --verbose         Show success messages"
    echo "  --help           Show this help"
    echo ""
    echo "Exit codes:"
    echo "  0 = Healthy"
    echo "  1 = Unhealthy"
    echo ""
    echo "Add to cron for monitoring:"
    echo "  */5 * * * * /opt/azure-test-api/deploy/health-check.sh --auto-restart"
}

case "${1:-}" in
    --help|-h)
        show_usage
        ;;
    *)
        main "$@"
        ;;
esac
