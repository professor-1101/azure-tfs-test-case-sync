# Azure Test Plan Import API

<div align="center">

**Enterprise-Grade REST API for Azure DevOps Test Plan Management**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Azure DevOps](https://img.shields.io/badge/Azure%20DevOps-Compatible-orange.svg)](https://azure.microsoft.com/services/devops/)

</div>

## Overview

Azure Test Plan Import API is a production-ready FastAPI application that provides intelligent test case management for Azure DevOps with advanced version management, automatic test plan creation, and enterprise-grade reliability.

### Key Features

- **Intelligent Version Management**: Automatic handling of Major/Minor/Patch/Same version changes
- **Background Processing**: Asynchronous import handling for large test suites  
- **Auto-Recovery**: Service auto-restart and health monitoring
- **Comprehensive Logging**: Detailed logging with automatic rotation
- **Multiple Authentication**: Support for NTLM and Personal Access Tokens
- **Modern API**: FastAPI with automatic OpenAPI documentation
- **Linux Native**: Systemd service with enterprise deployment features

## Version Management Logic

| Version Change Type | Behavior | Example |
|-------------------|----------|---------|
| **Major** (3.0.1 → 4.0.0) | Creates NEW test plan | Complete project restructure |
| **Minor** (3.0.1 → 3.1.0) | Creates NEW test plan | New feature additions |
| **Patch** (3.0.1 → 3.0.2) | Deletes old plan, creates new with updated content | Bug fixes and updates |
| **Same** (3.0.1 → 3.0.1) | Deletes old plan, creates fresh with new content | Content updates |

**Test Plan Naming**: `{project_name} Test Plan v{version}`

## Quick Installation

### Prerequisites
- Ubuntu/Debian 20.04+ or CentOS/RHEL 8+
- Python 3.9+, 2GB+ RAM, 10GB+ disk space
- sudo privileges and Azure DevOps server access

### Installation Steps

```bash
# Clone repository
git clone https://github.com/professor-1101/azure-tfs-test-case-sync.git
cd azure-tfs-test-case-sync

# Run automated installation
sudo bash deploy/install.sh

# Configure Azure DevOps settings
sudo nano /opt/azure-test-api/.env

# Start service
sudo systemctl start azure-test-api

# Verify installation
sudo /opt/azure-test-api/deploy/manage.sh status
```

## Deployment Scripts

### `deploy/install.sh` - Main Installation Script

Complete automated installation and setup:
- System dependency installation (Python, nginx, etc.)
- User creation (`azureapi` system user)
- Python virtual environment setup
- Application deployment to `/opt/azure-test-api`
- Systemd service installation and enabling
- Environment file generation and script permissions

### `deploy/manage.sh` - Service Management

```bash
# Service Control
sudo /opt/azure-test-api/deploy/manage.sh start      # Start service
sudo /opt/azure-test-api/deploy/manage.sh stop       # Stop service  
sudo /opt/azure-test-api/deploy/manage.sh restart    # Restart service
sudo /opt/azure-test-api/deploy/manage.sh status     # Show status
sudo /opt/azure-test-api/deploy/manage.sh logs       # Follow logs

# Maintenance
sudo /opt/azure-test-api/deploy/manage.sh install    # Install systemd service
sudo /opt/azure-test-api/deploy/manage.sh update     # Update application
sudo /opt/azure-test-api/deploy/manage.sh uninstall  # Remove service
```

### `deploy/health-check.sh` - Health Monitoring

Automated health monitoring with auto-recovery:
- Service status and API endpoint health checks
- Disk space and memory usage monitoring
- Automatic service restart on failure
- Auto-enable service for boot startup

```bash
# Manual health checks
./deploy/health-check.sh --verbose           # Detailed health check
./deploy/health-check.sh --auto-restart      # Health check with auto-restart

# Automated monitoring (add to cron)
*/5 * * * * /opt/azure-test-api/deploy/health-check.sh --auto-restart
```

### `deploy/fix-permissions.sh` - Permission Repair

Quick fix for script execution permissions:
```bash
sudo bash deploy/fix-permissions.sh
```

### Other Configuration Files

- **`azure-test-api.service`**: Systemd service with auto-restart configuration
- **`nginx.conf`**: Reverse proxy with security headers and SSL support
- **`requirements-production.txt`**: Optimized production dependencies
- **`env.example`**: Environment configuration template

## API Endpoints

### Health & Status
- `GET /health` - Basic health check
- `GET /api/v1/health` - Detailed health check with Azure DevOps connectivity
- `GET /info` - API information and configuration

### Import Operations
- `POST /api/v1/import/async` - Asynchronous test case import
- `GET /api/v1/import/status/{task_id}` - Check import task status

### Test Plan Management
- `GET /api/v1/test-plans/{project_name}` - List all test plans
- `POST /api/v1/debug/version-management` - Debug version management logic

## Authentication

### NTLM Authentication (Windows Domain)
```bash
curl -X POST "http://your-server:5050/api/v1/import/async" \
  -F "token=DOMAIN\\username:password" \
  -F "project_name=Test Process" \
  -F "version=2.0.0" \
  -F "file=@test_data.json"
```

### Personal Access Token (Recommended)
```bash
curl -X POST "http://your-server:5050/api/v1/import/async" \
  -F "token=:your_personal_access_token_here" \
  -F "project_name=Test Process" \
  -F "version=2.0.0" \
  -F "file=@test_data.json"
```

## Configuration

Edit `/opt/azure-test-api/.env`:

```bash
# Azure DevOps Server URL (Required)
AZURE_DEVOPS_ORG_URL=http://192.168.10.22:8080/tfs/RPKavoshDevOps

# Logging (Optional)
LOG_LEVEL=INFO
LOG_MAX_FILE_SIZE_MB=5
LOG_BACKUP_COUNT=3
LOG_CLEANUP_DAYS=7
```

**Important**: Authentication credentials (token/username/password) and project names are passed via API requests, not environment variables.

## Auto-Restart & Auto-Start

The service automatically:
- Restarts on failure (up to 5 attempts within 5 minutes)
- Starts on system boot
- Monitors health and recovers automatically

Check configuration:
```bash
sudo systemctl is-enabled azure-test-api    # Auto-start status
sudo /opt/azure-test-api/deploy/manage.sh status    # Full status check
```

## Monitoring & Health Checks

### Automated Monitoring
```bash
# Add to cron for continuous monitoring
*/5 * * * * /opt/azure-test-api/deploy/health-check.sh --auto-restart
```

### Manual Checks
```bash
# Service status
sudo systemctl status azure-test-api

# API health
curl http://your-server-ip:5050/health

# Recent logs
sudo journalctl -u azure-test-api -n 50

# Detailed health check
/opt/azure-test-api/deploy/health-check.sh --verbose
```

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
sudo systemctl status azure-test-api
sudo journalctl -u azure-test-api -f
sudo systemctl daemon-reload
sudo systemctl restart azure-test-api
```

#### Script Permission Errors
```bash
# Fix permissions
sudo bash deploy/fix-permissions.sh
# Or manually
sudo chmod +x /opt/azure-test-api/deploy/*.sh
```

#### Azure DevOps Connection Issues
```bash
# Test connectivity
curl -u "username:password" http://your-server:8080/tfs/Collection/_apis/projects
# Check configuration
sudo nano /opt/azure-test-api/.env
```

#### Port Issues
```bash
# Check port usage
sudo lsof -i :5050
sudo netstat -tulpn | grep :5050
```

#### Firewall Issues
```bash
# Allow port 5050
sudo ufw allow 5050/tcp
sudo iptables -A INPUT -p tcp --dport 5050 -j ACCEPT
```

### Log Locations
- **Application**: `/opt/azure-test-api/logs/`
- **Service**: `sudo journalctl -u azure-test-api`
- **Nginx**: `/var/log/nginx/azure-test-api.*`
- **Health Check**: `/var/log/azure-api-health.log`

## Security & Performance

### Security Best Practices
```bash
# Firewall configuration
sudo ufw allow 5050/tcp 80/tcp 443/tcp 22/tcp
sudo ufw enable

# SSL certificate (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com

# Secure environment file
sudo chmod 600 /opt/azure-test-api/.env
sudo chown azureapi:azureapi /opt/azure-test-api/.env
```

### Performance Tuning
```bash
# System optimization
echo "azureapi soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "azureapi hard nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "net.core.somaxconn = 1024" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Application tuning (edit .env)
API_WORKERS=4                    # 2 * CPU cores
REQUEST_TIMEOUT_SECONDS=300
WORKER_TIMEOUT_SECONDS=300
```

## Updates & Maintenance

### Updates
```bash
# Automatic update
sudo /opt/azure-test-api/deploy/manage.sh update

# Manual update
cd /opt/azure-test-api
sudo -u azureapi git pull origin main
sudo -u azureapi /opt/azure-test-api/venv/bin/pip install -r requirements.txt
sudo systemctl restart azure-test-api
```

### Backup
```bash
# Backup application
sudo tar -czf /backup/azure-api-$(date +%Y%m%d).tar.gz /opt/azure-test-api

# Backup configuration
sudo cp /opt/azure-test-api/.env /backup/
sudo cp /etc/systemd/system/azure-test-api.service /backup/
```

## Development

### Local Setup
```bash
git clone https://github.com/professor-1101/azure-tfs-test-case-sync.git
cd azure-tfs-test-case-sync
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Testing
```bash
pip install pytest pytest-asyncio httpx
pytest tests/
```

### API Documentation
- **Swagger UI**: `http://localhost:5050/docs`
- **ReDoc**: `http://localhost:5050/redoc`

## Support

- **Documentation**: This README
- **Issues**: [GitHub Issues](https://github.com/professor-1101/azure-tfs-test-case-sync/issues)
- **Contributing**: Fork → Branch → Commit → Push → Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built for Enterprise Azure DevOps Integration**

</div>