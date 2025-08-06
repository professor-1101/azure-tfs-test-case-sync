# Azure Test Plan Import API

<div align="center">

```
                            ███████████████████████████████████████████                             
                          ███████████████████████████████████████████████                           
                        ███████████████████████████████████████████████████                         
                      ███████████████████████████████████████████████████████                       
                    ███████████████████████████████████████████████████████████                     
                  ███████████████████████████████████████████████████████████████                   
                 ██████████████████████████████████████████████████████████████████                 
               ██████████████████████████████████████████████████████████████████████               
             █████████████████████████████████████████████████████████████████████████              
           █████████████████████████████████████████████████████████████████████████████            
         █████████████████████████████████████████████████████████████████████████████████          
        ███████████████████████████████████████████████████████████████████████████████████         
       █████████████████████████████████████████████████████████████████████████████████████        
       ██████████████████████████                                  █████████████████████████        
       ████████████████████████                                      ███████████████████████        
       ██████████████████████                                         ██████████████████████        
       ██████████████████████                                         ██████████████████████        
       ██████████████████████                                         ██████████████████████        
       ██████████████████████                                         ██████████████████████        
       ██████████████████████                                         ██████████████████████        
       ██████████████████████                                         ██████████████████████        
       ██████████████████████                                         ██████████████████████        
       ██████████████████████                                         ██████████████████████        
       ██████████████████████                                         ██████████████████████        
       ██████████████████████                      █████████████████████████████████████████        
       ██████████████████████                    ████████████████████████                           
       ██████████████████████                    ██████████████████████████                         
       ██████████████████████                    ████████████████████████████                       
       ██████████████████████                    ██████████████████████████████                     
       ██████████████████████                    ████████████████████████████████                   
       ██████████████████████                    █████████████████████████████████                  
       ██████████████████████                    ███████████████████████████████████                
       ██████████████████████                    █████████████████████████████████████              
       ██████████████████████                    ███████████████████████████████████████            
       ███████████████████████                   █████████████████████████████████████████          
       █████████████████████████                 ██████████████████████████████████████████         
       ██████████████████████████████████████████████████████████████████████████████████████       
        ███████████████████████████████████████████████████████████████                             
         █████████████████████████████████████████ ████████████████████                             
           ███████████████████████████████████████   ██████████████████                             
            ██████████████████████████████████████     ████████████████                             
              ████████████████████████████████████       ██████████████                             
                ██████████████████████████████████         ████████████                             
                  ████████████████████████████████          ███████████                             
                    ██████████████████████████████            █████████                             
                      ████████████████████████████              ███████                             
                       ███████████████████████████                █████                             
                         █████████████████████████                  ███                             
                           ███████████████████████                    █                             
```

**Enterprise-Grade REST API for Azure DevOps Test Plan Management**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Azure DevOps](https://img.shields.io/badge/Azure%20DevOps-Compatible-orange.svg)](https://azure.microsoft.com/services/devops/)

</div>

## 📖 Overview

Azure Test Plan Import API is a production-ready FastAPI application that provides intelligent test case management for Azure DevOps. It features advanced version management, automatic test plan creation, and enterprise-grade reliability.

### 🎯 Key Features

- **🔄 Intelligent Version Management**: Automatic handling of Major/Minor/Patch/Same version changes
- **🚀 Background Processing**: Asynchronous import handling for large test suites  
- **🛡️ Auto-Recovery**: Service auto-restart and health monitoring
- **📊 Comprehensive Logging**: Detailed logging with automatic rotation
- **🔐 Multiple Authentication**: Support for NTLM and Personal Access Tokens
- **📱 Modern API**: FastAPI with automatic OpenAPI documentation
- **🐧 Linux Native**: Systemd service with enterprise deployment features

## 🔄 Version Management Logic

The API implements intelligent version management for test plans and suites:

| Version Change Type | Behavior | Example |
|-------------------|----------|---------|
| **Major** (3.0.1 → 4.0.0) | ✅ Creates **NEW** test plan | Complete project restructure |
| **Minor** (3.0.1 → 3.1.0) | ✅ Creates **NEW** test plan | New feature additions |
| **Patch** (3.0.1 → 3.0.2) | 🔄 **Deletes old** plan, **creates new** with updated content | Bug fixes and updates |
| **Same** (3.0.1 → 3.0.1) | 🔄 **Deletes old** plan, **creates fresh** with new content | Content updates |

### 📝 Test Plan Naming Convention
- Format: `{project_name} Test Plan v{version}`
- Example: `Test Process Test Plan v2.1.0`

## 🚀 Quick Start

### 📋 Prerequisites
- **OS**: Ubuntu/Debian 20.04+ or CentOS/RHEL 8+
- **Python**: 3.9 or higher
- **Memory**: 2GB+ RAM recommended
- **Storage**: 10GB+ disk space
- **Access**: sudo privileges required
- **Network**: Access to Azure DevOps server

### ⚡ One-Command Installation

```bash
# Clone the repository
git clone https://github.com/professor-1101/azure-tfs-test-case-sync.git
cd azure-tfs-test-case-sync

# Run the automated installation script
sudo bash deploy/install.sh

# Configure your Azure DevOps settings
sudo nano /opt/azure-test-api/.env

# Start the service
sudo systemctl start azure-test-api

# Verify installation
sudo /opt/azure-test-api/deploy/manage.sh status
```

**🎉 Your API is now running with auto-restart and auto-start features!**

## 🛠️ Deployment Scripts Reference

### 📄 `deploy/install.sh` - Main Installation Script

**Purpose**: Complete automated installation and setup of the Azure Test Plan Import API.

**Features**:
- ✅ System dependency installation (Python, nginx, etc.)
- ✅ User creation (`azureapi` system user)
- ✅ Python virtual environment setup
- ✅ Application deployment to `/opt/azure-test-api`
- ✅ Systemd service installation and enabling
- ✅ Automatic script permissions setup
- ✅ Environment file generation
- ✅ Auto-restart configuration

**Usage**:
```bash
sudo bash deploy/install.sh
```

**What it does**:
1. Updates system packages
2. Installs Python, pip, nginx, git, curl
3. Creates dedicated `azureapi` system user
4. Sets up application directory structure
5. Creates Python virtual environment
6. Installs Python dependencies
7. Creates and configures systemd service
8. Sets up logging directories
9. Generates environment configuration template
10. Enables auto-start on boot

### 🎛️ `deploy/manage.sh` - Service Management Script

**Purpose**: Complete service lifecycle management with beautiful interface.

**Commands**:

```bash
# Service Control
sudo /opt/azure-test-api/deploy/manage.sh start      # Start the API service
sudo /opt/azure-test-api/deploy/manage.sh stop       # Stop the API service  
sudo /opt/azure-test-api/deploy/manage.sh restart    # Restart the API service
sudo /opt/azure-test-api/deploy/manage.sh status     # Show detailed status
sudo /opt/azure-test-api/deploy/manage.sh logs       # Follow real-time logs

# Maintenance Operations
sudo /opt/azure-test-api/deploy/manage.sh install    # Install systemd service
sudo /opt/azure-test-api/deploy/manage.sh uninstall  # Remove systemd service
sudo /opt/azure-test-api/deploy/manage.sh update     # Update application code
sudo /opt/azure-test-api/deploy/manage.sh help       # Show help with ASCII art
```

**Status Information**:
- ✅ Service running status
- ✅ API endpoint health check
- ✅ Auto-start configuration verification
- ✅ Recent logs display
- ✅ Server IP detection and URL display

**Features**:
- 🎨 Beautiful ASCII art interface
- 🔍 Comprehensive health checking
- 📡 Automatic IP detection and URL display
- 🔄 Git-based application updates
- 📊 Real-time status monitoring

### 💊 `deploy/health-check.sh` - Health Monitoring Script

**Purpose**: Automated health monitoring with auto-recovery capabilities.

**Usage**:
```bash
# Manual health checks
./deploy/health-check.sh --verbose           # Detailed health check
./deploy/health-check.sh --auto-restart      # Health check with auto-restart
./deploy/health-check.sh --help              # Show help with ASCII art

# Automated monitoring (recommended)
# Add to cron for continuous monitoring
*/5 * * * * /opt/azure-test-api/deploy/health-check.sh --auto-restart
```

**Health Checks Performed**:
- 🔍 **Service Status**: Systemd service running state
- 🌐 **API Health**: HTTP health endpoint response
- 🚀 **API Functionality**: Core endpoint accessibility
- 💾 **Disk Space**: Storage usage monitoring
- 🧠 **Memory Usage**: Process memory consumption
- ⚙️ **Auto-start**: Service enable status verification

**Auto-Recovery Actions**:
- 🔄 Automatic service restart on failure
- ⚡ Auto-enable service for boot startup
- 📝 Comprehensive logging of all actions
- 🚨 Configurable retry attempts and intervals

**Log Location**: `/var/log/azure-api-health.log`

### 🔧 `deploy/fix-permissions.sh` - Permission Repair Script

**Purpose**: Quick fix for script execution permissions.

**Usage**:
```bash
# Fix permissions for all deployment scripts
sudo bash deploy/fix-permissions.sh
```

**What it fixes**:
- ✅ Makes all `.sh` files in `deploy/` executable
- ✅ Fixes permissions in `/opt/azure-test-api/deploy/`
- ✅ Provides clear guidance for script execution

### ⚙️ `deploy/azure-test-api.service` - Systemd Service Configuration

**Purpose**: Production-grade systemd service definition with auto-restart capabilities.

**Key Features**:
- 🔄 **Auto-restart**: `Restart=always` with intelligent retry logic
- ⏰ **Restart Delay**: 10-second delay between restart attempts
- 🔢 **Retry Limits**: Maximum 5 restart attempts within 5 minutes
- 🚀 **Auto-start**: Enabled for automatic boot startup
- 🔒 **Security**: Runs as dedicated `azureapi` user with restricted permissions
- 📊 **Resource Limits**: Memory and file descriptor limits
- 📝 **Logging**: Separate access and error logs

**Service Configuration**:
```ini
[Unit]
Description=Azure Test Plan Import API
After=network.target

[Service]
Type=exec
User=azureapi
Group=azureapi
WorkingDirectory=/opt/azure-test-api
ExecStart=/opt/azure-test-api/venv/bin/gunicorn main:app \
    --bind 0.0.0.0:5050 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker
Restart=always
RestartSec=10
StartLimitBurst=5
StartLimitInterval=300

[Install]
WantedBy=multi-user.target
```

### 🌐 `deploy/nginx.conf` - Reverse Proxy Configuration

**Purpose**: Production-ready Nginx reverse proxy with security headers and SSL support.

**Features**:
- 🔒 **Security Headers**: XSS protection, content type validation
- 🗜️ **Compression**: Gzip compression for better performance
- ⏱️ **Timeouts**: Optimized timeout settings for large uploads
- 📁 **File Uploads**: Support for large test case files (100MB limit)
- 🔐 **SSL Ready**: Commented SSL configuration for Let's Encrypt
- 📊 **Logging**: Separate access and error logs

**Installation**:
```bash
# Copy to Nginx sites
sudo cp /opt/azure-test-api/deploy/nginx.conf /etc/nginx/sites-available/azure-test-api

# Enable the site
sudo ln -s /etc/nginx/sites-available/azure-test-api /etc/nginx/sites-enabled/

# Test and restart Nginx
sudo nginx -t
sudo systemctl restart nginx
```

### 📦 `deploy/requirements-production.txt` - Production Dependencies

**Purpose**: Optimized Python dependencies for production deployment.

**Key Dependencies**:
- 🚀 **FastAPI**: Modern web framework
- 🦄 **Uvicorn/Gunicorn**: ASGI server with worker management  
- 🔗 **Requests**: HTTP client with NTLM authentication
- 🔒 **Cryptography**: Security and encryption support
- ⚡ **UVLoop**: High-performance async event loop
- 📊 **Psutil**: System monitoring capabilities

### 📋 `deploy/env.example` - Configuration Template

**Purpose**: Complete environment variable template with examples.

**Configuration Categories**:
- 🔗 **Azure DevOps**: Server URL, project settings
- 🔑 **Authentication**: NTLM credentials or Personal Access Tokens
- 🌐 **API Settings**: Host, port, worker configuration
- 📝 **Logging**: Log levels, file rotation settings
- 🔒 **Security**: Secret keys and encryption settings
- ⚡ **Performance**: Timeout, worker, and resource limits

## 📡 API Endpoints

### 🏥 Health & Status

```http
GET /health
```
Basic health check endpoint.

```http
GET /api/v1/health  
```
Detailed health check with Azure DevOps connectivity.

```http
GET /info
```
API information and configuration details.

### 📥 Import Operations

```http
POST /api/v1/import/async
```
**Asynchronous test case import** (recommended for large files)

**Parameters**:
- `file`: JSON test case file
- `token`: Authentication token (format: `username:password` or `:PAT`)
- `project_name`: Azure DevOps project name
- `version`: Semantic version (e.g., `2.1.0`)

**Response**:
```json
{
  "task_id": "uuid-task-identifier",
  "status": "starting",
  "message": "Import task created"
}
```

```http
GET /api/v1/import/status/{task_id}
```
**Check import task status**

**Response**:
```json
{
  "task_id": "uuid-task-identifier",
  "status": "completed",
  "progress": 100,
  "result": {
    "created": 45,
    "errors": 0
  },
  "logs": ["Task started...", "Import completed"]
}
```

### 📋 Test Plan Management

```http
GET /api/v1/test-plans/{project_name}
```
**List all test plans** for a project

```http
POST /api/v1/debug/version-management
```
**Debug version management logic** (development endpoint)

## 🔑 Authentication

### 🏢 NTLM Authentication (Windows Domain)
```bash
curl -X POST "http://your-server:5050/api/v1/import/async" \
  -F "token=DOMAIN\\username:password" \
  -F "project_name=Test Process" \
  -F "version=2.0.0" \
  -F "file=@test_data.json"
```

### 🔐 Personal Access Token (Recommended)
```bash
curl -X POST "http://your-server:5050/api/v1/import/async" \
  -F "token=:your_personal_access_token_here" \
  -F "project_name=Test Process" \
  -F "version=2.0.0" \
  -F "file=@test_data.json"
```

## 📊 Configuration

### 📝 Environment Variables

Create and edit `/opt/azure-test-api/.env`:

```bash
# Azure DevOps Configuration
AZURE_DEVOPS_ORG_URL=http://192.168.10.22:8080/tfs/RPKavoshDevOps
AZURE_DEVOPS_PROJECT_NAME=Test Process

# Authentication (choose one method)
AZURE_DEVOPS_USERNAME=DOMAIN\\username
AZURE_DEVOPS_PASSWORD=password
# OR
AZURE_DEVOPS_PAT=your_personal_access_token

# API Server Settings
API_HOST=0.0.0.0
API_PORT=5050
API_WORKERS=4

# Logging Configuration
LOG_LEVEL=INFO
LOG_MAX_FILE_SIZE_MB=10
LOG_BACKUP_COUNT=5
LOG_CLEANUP_DAYS=30

# Security
SECRET_KEY=your-generated-secret-key

# Performance Tuning
MAX_UPLOAD_SIZE_MB=100
REQUEST_TIMEOUT_SECONDS=300
WORKER_TIMEOUT_SECONDS=300
```

## 🔄 Auto-Restart & Auto-Start Features

### 🔄 Automatic Service Restart

The service automatically restarts if it crashes:

```bash
# Systemd restart configuration
Restart=always                 # Always restart on failure
RestartSec=10                  # Wait 10 seconds before restart
StartLimitBurst=5              # Maximum 5 restart attempts
StartLimitInterval=300         # Within 5 minutes
```

### 🚀 Auto-Start on System Boot

The service automatically starts when the server boots:

```bash
# Check auto-start status
sudo systemctl is-enabled azure-test-api

# Enable auto-start (done automatically during installation)
sudo systemctl enable azure-test-api

# Disable auto-start (if needed)
sudo systemctl disable azure-test-api
```

### 📊 Service Status Check

```bash
# Comprehensive status check
sudo /opt/azure-test-api/deploy/manage.sh status

# Expected output:
# ✓ Service is running
# ✓ API is responding  
# ✓ Service is enabled (will start on boot)
```

## 📊 Monitoring & Health Checks

### 🔍 Automated Health Monitoring

Set up continuous monitoring with automatic recovery:

```bash
# Add to cron for monitoring every 5 minutes
sudo crontab -e

# Add this line:
*/5 * * * * /opt/azure-test-api/deploy/health-check.sh --auto-restart
```

### 🎯 What Health Monitoring Does

- ✅ **Service Monitoring**: Checks if systemd service is running
- ✅ **API Testing**: Verifies API endpoints are responding
- ✅ **Resource Monitoring**: Tracks disk space and memory usage
- ✅ **Auto-Recovery**: Automatically restarts unhealthy services
- ✅ **Boot Configuration**: Ensures auto-start is enabled
- ✅ **Detailed Logging**: Records all monitoring activities

### 📊 Manual Health Checks

```bash
# Detailed health check
/opt/azure-test-api/deploy/health-check.sh --verbose

# Check API endpoints directly
curl http://your-server-ip:5050/health

# Check service status
sudo systemctl status azure-test-api

# View recent logs
sudo journalctl -u azure-test-api -n 50
```

## 🔍 Troubleshooting

### ❌ Common Issues & Solutions

#### 1. **Service Won't Start**
```bash
# Check service status and logs
sudo systemctl status azure-test-api
sudo journalctl -u azure-test-api -f

# Common fixes
sudo systemctl daemon-reload
sudo systemctl restart azure-test-api
```

#### 2. **Script Permission Errors**
```bash
# Error: "./manage.sh: command not found"
# Solution: Fix permissions
sudo bash deploy/fix-permissions.sh

# Or manually
sudo chmod +x /opt/azure-test-api/deploy/*.sh
```

#### 3. **Azure DevOps Connection Issues**
```bash
# Test connectivity directly
curl -u "username:password" \
  http://your-server:8080/tfs/Collection/_apis/projects

# Check configuration
sudo nano /opt/azure-test-api/.env
```

#### 4. **Port Already in Use**
```bash
# Check what's using port 5050
sudo lsof -i :5050
sudo netstat -tulpn | grep :5050

# Kill process if necessary
sudo kill -9 PID
```

#### 5. **High Memory Usage**
```bash
# Restart service
sudo systemctl restart azure-test-api

# Reduce worker count in .env
API_WORKERS=2  # Default is 4
```

#### 6. **Firewall Blocking Access**
```bash
# Allow port 5050
sudo ufw allow 5050/tcp

# For iptables
sudo iptables -A INPUT -p tcp --dport 5050 -j ACCEPT
```

### 📂 Log Locations

- **Application Logs**: `/opt/azure-test-api/logs/`
- **Service Logs**: `sudo journalctl -u azure-test-api`
- **Nginx Logs**: `/var/log/nginx/azure-test-api.*`
- **Health Check Logs**: `/var/log/azure-api-health.log`

## 🔐 Security Best Practices

### 🛡️ Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 5050/tcp    # API port
sudo ufw allow 80/tcp      # HTTP (if using nginx)
sudo ufw allow 443/tcp     # HTTPS (if using nginx)
sudo ufw allow 22/tcp      # SSH

# Enable firewall
sudo ufw enable
```

### 🔒 SSL Certificate Setup (Recommended for Production)

```bash
# Install Certbot for Let's Encrypt
sudo apt install certbot python3-certbot-nginx

# Generate SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal (usually automatic)
sudo systemctl enable certbot.timer
```

### 🔑 Environment Security

```bash
# Secure configuration file
sudo chown azureapi:azureapi /opt/azure-test-api/.env
sudo chmod 600 /opt/azure-test-api/.env

# Use strong secret keys
openssl rand -hex 32  # Generate secret key
```

## ⚡ Performance Tuning

### 🚀 System Optimization

```bash
# Increase file limits for high-load scenarios
echo "azureapi soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "azureapi hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize kernel parameters
echo "net.core.somaxconn = 1024" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### ⚙️ Application Tuning

Edit `/opt/azure-test-api/.env`:

```bash
# Worker Configuration (adjust based on CPU cores)
API_WORKERS=4                    # Recommended: 2 * CPU cores

# Timeout Settings
REQUEST_TIMEOUT_SECONDS=300      # API request timeout
WORKER_TIMEOUT_SECONDS=300       # Worker process timeout

# File Upload Limits
MAX_UPLOAD_SIZE_MB=100          # Maximum file size

# Logging Performance
LOG_LEVEL=INFO                   # Use INFO for production
LOG_MAX_FILE_SIZE_MB=10         # Rotate logs at 10MB
LOG_BACKUP_COUNT=5              # Keep 5 backup files
```

### 🧠 Memory Optimization

```bash
# Monitor memory usage
sudo /opt/azure-test-api/deploy/health-check.sh --verbose

# Adjust worker count if needed
# Rule of thumb: 1 worker per 256MB RAM available
```

## 🆙 Updates & Maintenance

### 🔄 Automatic Updates

```bash
# Update application using management script
sudo /opt/azure-test-api/deploy/manage.sh update

# Manual update process
cd /opt/azure-test-api
sudo -u azureapi git pull origin main
sudo -u azureapi /opt/azure-test-api/venv/bin/pip install -r requirements.txt
sudo systemctl restart azure-test-api
```

### 💾 Backup & Recovery

```bash
# Backup application data
sudo tar -czf /backup/azure-api-$(date +%Y%m%d).tar.gz \
  /opt/azure-test-api

# Backup configuration
sudo cp /opt/azure-test-api/.env /backup/

# Backup systemd service
sudo cp /etc/systemd/system/azure-test-api.service /backup/
```

### 📊 System Maintenance

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Clean old logs
sudo /opt/azure-test-api/deploy/health-check.sh --verbose

# Check disk space
df -h /opt/azure-test-api
```

## 📚 Development & Testing

### 🧪 Local Development

```bash
# Clone repository
git clone https://github.com/professor-1101/azure-tfs-test-case-sync.git
cd azure-tfs-test-case-sync

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python main.py
```

### 🔍 API Testing

```bash
# Health check
curl http://localhost:5050/health

# API documentation
# Visit: http://localhost:5050/docs

# Test import (replace with your data)
curl -X POST "http://localhost:5050/api/v1/import/async" \
  -F "token=:your_token" \
  -F "project_name=Test Project" \
  -F "version=1.0.0" \
  -F "file=@test_data.json"
```

### 📋 Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/

# Run specific test
pytest tests/test_api.py -v
```

## 📞 Support & Contributing

### 🆘 Getting Help

- **📖 Documentation**: This README
- **🐛 Issues**: [GitHub Issues](https://github.com/professor-1101/azure-tfs-test-case-sync/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/professor-1101/azure-tfs-test-case-sync/discussions)

### 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 🙏 Acknowledgments

- FastAPI team for the excellent framework
- Azure DevOps team for comprehensive APIs
- Open source community for invaluable tools and libraries

---

<div align="center">

**Built with ❤️ for Enterprise Azure DevOps Integration**

</div>