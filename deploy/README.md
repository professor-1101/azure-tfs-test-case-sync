# Azure Test Plan Import API - Deployment Guide

Complete guide for deploying the Azure Test Plan Import API on Linux servers.

## 🚀 Quick Start

### Prerequisites
- Ubuntu/Debian 20.04+ or CentOS/RHEL 8+
- Python 3.9+
- sudo access
- 2GB+ RAM
- 10GB+ disk space

### One-Command Installation
```bash
# Clone repository
git clone https://github.com/professor-1101/azure-tfs-test-case-sync.git
cd azure-tfs-test-case-sync

# Run installation script
sudo bash deploy/install.sh
```

## 📋 Manual Installation Steps

### 1. System Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv nginx git curl

# Create user
sudo useradd --system --shell /bin/bash --home-dir /opt/azure-test-api --create-home azureapi
```

### 2. Application Setup
```bash
# Clone application
sudo git clone https://github.com/professor-1101/azure-tfs-test-case-sync.git /opt/azure-test-api
sudo chown -R azureapi:azureapi /opt/azure-test-api

# Setup Python environment
sudo -u azureapi python3 -m venv /opt/azure-test-api/venv
sudo -u azureapi /opt/azure-test-api/venv/bin/pip install -r /opt/azure-test-api/deploy/requirements-production.txt
sudo -u azureapi /opt/azure-test-api/venv/bin/pip install gunicorn
```

### 3. Configuration
```bash
# Create environment file
sudo cp /opt/azure-test-api/deploy/env.example /opt/azure-test-api/.env
sudo chown azureapi:azureapi /opt/azure-test-api/.env
sudo chmod 600 /opt/azure-test-api/.env

# Edit configuration
sudo nano /opt/azure-test-api/.env
```

**Required settings in .env:**
```bash
AZURE_DEVOPS_ORG_URL=http://your-server:8080/tfs/YourCollection
AZURE_DEVOPS_PROJECT_NAME=YourProject
AZURE_DEVOPS_USERNAME=YourDomain\\YourUsername
AZURE_DEVOPS_PASSWORD=YourPassword
SECRET_KEY=$(openssl rand -hex 32)
```

### 4. Service Installation
```bash
# Install systemd service
sudo cp /opt/azure-test-api/deploy/azure-test-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable azure-test-api

# Start service
sudo systemctl start azure-test-api
```

### 5. Nginx Setup (Optional)
```bash
# Copy nginx config
sudo cp /opt/azure-test-api/deploy/nginx.conf /etc/nginx/sites-available/azure-test-api
sudo ln -s /etc/nginx/sites-available/azure-test-api /etc/nginx/sites-enabled/

# Edit server name
sudo nano /etc/nginx/sites-available/azure-test-api

# Test and reload nginx
sudo nginx -t
sudo systemctl restart nginx
```

## 🔧 Management Commands

The `manage.sh` script provides easy service management:

```bash
# Make executable
chmod +x /opt/azure-test-api/deploy/manage.sh

# Service operations
sudo ./deploy/manage.sh start      # Start service
sudo ./deploy/manage.sh stop       # Stop service
sudo ./deploy/manage.sh restart    # Restart service
sudo ./deploy/manage.sh status     # Show status
sudo ./deploy/manage.sh logs       # Follow logs

# Maintenance
sudo ./deploy/manage.sh install    # Install systemd service
sudo ./deploy/manage.sh update     # Update application
sudo ./deploy/manage.sh uninstall  # Remove service
```

## 🐳 Docker Deployment

### Using Docker Compose
```bash
# Create environment file
cp deploy/env.example deploy/.env
# Edit deploy/.env with your settings

# Start services
cd deploy
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f azure-test-api
```

### Manual Docker
```bash
# Build image
docker build -f deploy/Dockerfile -t azure-test-api .

# Run container
docker run -d \
  --name azure-test-api \
  -p 5050:5050 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/.env:/app/.env:ro \
  azure-test-api
```

## 📊 Monitoring & Health Checks

### Automated Health Monitoring
```bash
# Make health check executable
chmod +x /opt/azure-test-api/deploy/health-check.sh

# Add to cron for monitoring (every 5 minutes)
sudo crontab -e
```

Add this line:
```cron
*/5 * * * * /opt/azure-test-api/deploy/health-check.sh --auto-restart
```

### Manual Health Check
```bash
# Check service health
./deploy/health-check.sh --verbose

# Check API endpoint (replace with your server IP)
curl http://your-server-ip:5050/health

# Check service status
sudo systemctl status azure-test-api
```

## 🔍 Troubleshooting

### Common Issues

1. **Service won't start**
   ```bash
   sudo journalctl -u azure-test-api -f
   sudo systemctl status azure-test-api
   ```

2. **Permission errors**
   ```bash
   sudo chown -R azureapi:azureapi /opt/azure-test-api
   sudo chmod +x /opt/azure-test-api/deploy/*.sh
   ```

3. **Azure DevOps connection issues**
   ```bash
   # Test connectivity
   curl -u "username:password" http://your-server:8080/tfs/Collection/_apis/projects
   ```

4. **High memory usage**
   ```bash
   # Restart service
   sudo systemctl restart azure-test-api
   
   # Check worker count in .env
   API_WORKERS=2  # Reduce if needed
   ```

### Log Locations
- **Application logs**: `/opt/azure-test-api/logs/`
- **Service logs**: `sudo journalctl -u azure-test-api`
- **Nginx logs**: `/var/log/nginx/azure-test-api.*`
- **Health check logs**: `/var/log/azure-api-health.log`

## 🔐 Security Considerations

1. **Firewall Configuration**
   ```bash
   sudo ufw allow 5050/tcp  # API port
   sudo ufw allow 80/tcp    # HTTP (if using nginx)
   sudo ufw allow 443/tcp   # HTTPS (if using nginx)
   ```

2. **SSL Certificate** (Recommended for production)
   ```bash
   # Using Let's Encrypt
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

3. **Environment Security**
   ```bash
   # Secure .env file
   sudo chmod 600 /opt/azure-test-api/.env
   sudo chown azureapi:azureapi /opt/azure-test-api/.env
   ```

## 📈 Performance Tuning

### System Optimization
```bash
# Increase file limits
echo "azureapi soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "azureapi hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize kernel parameters
echo "net.core.somaxconn = 1024" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### Application Tuning
Edit `/opt/azure-test-api/.env`:
```bash
API_WORKERS=4              # Adjust based on CPU cores
REQUEST_TIMEOUT_SECONDS=300
WORKER_TIMEOUT_SECONDS=300
MAX_UPLOAD_SIZE_MB=100
```

## 🆙 Updates & Maintenance

### Automatic Updates
```bash
# Update application
sudo ./deploy/manage.sh update

# Update system packages
sudo apt update && sudo apt upgrade -y
```

### Backup
```bash
# Backup application data
sudo tar -czf /backup/azure-api-$(date +%Y%m%d).tar.gz /opt/azure-test-api

# Backup database (if applicable)
# sudo -u azureapi pg_dump database_name > /backup/db-$(date +%Y%m%d).sql
```

## 📞 Support

- **Documentation**: [GitHub Repository](https://github.com/professor-1101/azure-tfs-test-case-sync)
- **Issues**: [GitHub Issues](https://github.com/professor-1101/azure-tfs-test-case-sync/issues)
- **API Documentation**: `http://your-server:5050/docs`
