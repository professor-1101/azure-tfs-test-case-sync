import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.api.v1.endpoints import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Starting Azure DevOps Test Plan Import API")
    logger.info(f"Version: {settings.version}")
    logger.info(f"Azure DevOps URL: {settings.azure_devops_org_url}")
    logger.info("Ready to process requests for any Azure DevOps project")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Azure DevOps Test Plan Import API")


logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    lifespan=lifespan,
    title=settings.project_name,
    description="""
# Azure DevOps Test Plan Import API

This API allows you to import test cases from JSON content to Azure DevOps Test Plans with version management.

## 🔄 Version Management Logic
- **Major** (مثل 3.0.1 → 4.0.0): همیشه **تست پلن جدید** ساخته می‌شود
- **Minor** (مثل 3.0.1 → 3.1.0): همیشه **تست پلن جدید** ساخته می‌شود  
- **Patch** (مثل 3.0.1 → 3.0.2): از **همان test plan موجود** استفاده می‌شود و **محتوای جدید** به آن اضافه می‌شود
- **Same** (مثل 3.0.1 با خودش): محتوای تست پلن موجود **به‌روزرسانی** می‌شود

## 📋 Test Plan Naming
- Format: `{project_name} Test Plan v{version}`
- Example: `Test Process Test Plan v2.0.0`

## 🚀 Quick Start

1. **Health Check**: Verify API is running
   ```
   GET /api/v1/health
   ```

2. **Import Test Cases**: Main endpoint for versioned imports
   ```
   POST /api/v1/import/versioned
   ```

3. **List Test Plans**: Check available test plans
   ```
   GET /api/v1/test-plans/{project_name}
   ```

## 📝 Example Request

```json
{
  "project_name": "Test Process",
  "token": "username:password",
  "version": "2.0.0",
  "content": {
    "name": "پست بانک",
    "features": [...]
  }
}
```

## 🔧 Configuration

The API uses the following environment variables:
- `AZURE_DEVOPS_ORG_URL`: Azure DevOps organization URL
- `AZURE_DEVOPS_PROJECT`: Default project name
- `AZURE_DEVOPS_TEST_PLAN`: Default test plan name
- `AZURE_DEVOPS_TEST_SUITE`: Default test suite name
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)

## 📚 Documentation

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`

## 🧪 Testing

Run the test files to verify functionality:
- `test_simple.py`: Basic functionality test
- `test_versioned.py`: Comprehensive multi-version test
- `test_validation.py`: Input validation test

## 🔍 Troubleshooting

1. **401 Unauthorized**: Check your authentication token format
2. **404 Not Found**: Verify endpoint URL and API version
3. **500 Internal Server Error**: Check Azure DevOps connection and permissions

## 📊 Health Check Response

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "azure_devops_connected": true
}
```

## 🔗 API Info Response

```json
{
  "name": "Azure DevOps Test Plan Import API",
  "version": "1.0.0",
  "description": "API for importing Gherkin features to Azure DevOps Test Plans",
  "endpoints": {
    "health": "/api/v1/health",
    "import_versioned": "/api/v1/import/versioned",
    "import_json": "/api/v1/import/json",
    "import_file": "/api/v1/import/file",
    "list_test_plans": "/api/v1/test-plans/{project_name}"
  },
  "configuration": {
    "org_url": "http://192.168.10.22:8080/tfs/RPKavoshDevOps",
    "project": "Test Process",
    "api_version": "5.0"
  }
}
```
""",
    version=settings.version,
    contact={
        "name": "API Support",
        "email": "support@example.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Azure DevOps Test Plan Import API",
        "version": settings.version,
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.get("/info")
async def info():
    """API information endpoint."""
    return {
        "name": settings.project_name,
        "version": settings.version,
        "description": settings.description,
        "endpoints": {
            "health": "/api/v1/health",
            "import_versioned": "/api/v1/import/versioned",
            "import_json": "/api/v1/import/json",
            "import_file": "/api/v1/import/file",
            "list_test_plans": "/api/v1/test-plans/{project_name}"
        },
        "configuration": {
            "org_url": settings.azure_devops_org_url,
            "project": settings.azure_devops_project,
            "api_version": settings.azure_devops_api_version
        }
    }


if __name__ == "__main__":
    import socket
    
    # Auto-detect local IP address
    def get_local_ip():
        try:
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            # Fallback to localhost if detection fails
            return "127.0.0.1"
    
    host_ip = get_local_ip()
    port = 5050
    
    print(f"🚀 Starting Azure Test Plan Import API...")
    print(f"📡 Server will be available at: http://{host_ip}:{port}")
    print(f"📖 API Documentation: http://{host_ip}:{port}/docs")
    print(f"🔍 Health Check: http://{host_ip}:{port}/health")
    print(f"ℹ️  API Info: http://{host_ip}:{port}/info")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level=settings.log_level.lower()
    )
