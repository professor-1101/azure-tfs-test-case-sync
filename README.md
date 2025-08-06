# 🚀 Azure DevOps Test Plan Import API

یک API مبتنی بر FastAPI برای import کردن test cases از فایل‌های JSON به Azure DevOps Test Plans با مدیریت هوشمند versioning.

## ✨ ویژگی‌های اصلی

- 📋 **Import خودکار test cases** از فایل‌های JSON
- 🔄 **مدیریت هوشمند versioning** با منطق Major/Minor/Patch/Same
- 🏗️ **مدیریت test plans و test suites** با ساختار سازماندهی شده
- 🔐 **پشتیبانی از NTLM و Basic Authentication** برای Azure DevOps
- ⚡ **Background task processing** با real-time progress tracking
- 📝 **Log management هوشمند** با rotation و cleanup خودکار
- 📚 **API Documentation کامل** با Swagger UI و ReDoc
- 🌐 **RESTful API** با response models استاندارد

## 📊 منطق Version Management

| نوع تغییر | مثال | رفتار |
|----------|-------|--------|
| **Major** | `3.0.1 → 4.0.0` | همیشه **تست پلن جدید** ساخته می‌شود |
| **Minor** | `3.0.1 → 3.1.0` | همیشه **تست پلن جدید** ساخته می‌شود |
| **Patch** | `3.0.1 → 3.0.2` | از **همان test plan موجود** استفاده می‌شود و **محتوای جدید** به آن اضافه می‌شود |
| **Same** | `3.0.1 → 3.0.1` | **محتوای تست پلن موجود به‌روزرسانی** می‌شود |

## 🛠️ نصب و راه‌اندازی

### 1. نصب Dependencies

```bash
pip install -r requirements.txt
```

### 2. تنظیمات Environment Variables

```bash
# Azure DevOps Configuration
export AZURE_DEVOPS_ORG_URL="http://192.168.10.22:8080/tfs/RPKavoshDevOps"
export AZURE_DEVOPS_PROJECT="Test Process"

# API Configuration
export LOG_LEVEL="INFO"
export LOG_MAX_FILE_SIZE_MB="5"
export LOG_BACKUP_COUNT="3" 
export LOG_CLEANUP_DAYS="7"
```

### 3. اجرای API

```bash
python main.py
```

API روی پورت **5050** در دسترس خواهد بود:
- **Base URL**: `http://localhost:5050`
- **Swagger UI**: `http://localhost:5050/docs`
- **ReDoc**: `http://localhost:5050/redoc`

## 📡 API Endpoints

### 🔍 Health & Info
- `GET /` - اطلاعات کلی API
- `GET /info` - جزئیات configuration و endpoints
- `GET /api/v1/health` - بررسی سلامت API

### 📋 Import Operations
- `POST /api/v1/import/async` - Import async test cases با version management
- `GET /api/v1/import/status/{task_id}` - بررسی وضعیت task های async

### 🐛 Debug & Monitoring  
- `GET /api/v1/import/debug/tasks` - لیست تمام tasks
- `GET /api/v1/import/debug/version/{project_name}/{version}` - تست منطق versioning
- `GET /api/v1/test-plans/{project_name}` - لیست test plans موجود
- `GET /api/v1/logs/{lines}` - مشاهده آخرین log ها

## 🔐 Authentication

### NTLM Authentication
```bash
# Format: username:password
curl -X POST "http://localhost:5050/api/v1/import/async" \
  -F "token=RPK\\ASadeghianAzar:iLAus1101" \
  -F "project_name=Test Process" \
  -F "version=1.0.0" \
  -F "file=@test_data.json"
```

### Basic Auth (PAT)
```bash
# Format: :personal_access_token
curl -X POST "http://localhost:5050/api/v1/import/async" \
  -F "token=:your_personal_access_token_here" \
  -F "project_name=Test Process" \
  -F "version=2.0.0" \
  -F "file=@test_data.json"
```

## 📝 نمونه Request/Response

### Import Async Request
```bash
curl -X POST "http://localhost:5050/api/v1/import/async" \
  -F "file=@test_cases.json" \
  -F "project_name=My Project" \
  -F "token=username:password" \
  -F "version=1.2.3"
```

### Response
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "started", 
  "message": "Import task started successfully. Use the status endpoint to check progress."
}
```

### Status Check
```bash
curl "http://localhost:5050/api/v1/import/status/550e8400-e29b-41d4-a716-446655440000"
```

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "progress": 75,
  "result": null,
  "error": null,
  "logs": [
    "[14:30:15] Task started",
    "[14:30:16] Version 1.2.3 detected as patch type",
    "[14:30:17] Processing 5 features...",
    "[14:30:18] Importing test cases..."
  ]
}
```

## 📁 ساختار فایل JSON

```json
{
  "name": "Sample Test Suite",
  "features": [
    {
      "name": "User Authentication",
      "scenarios": [
        {
          "name": "Login with valid credentials",
          "type": "scenario",
          "description": "Test user login functionality",
          "steps": [
            {
              "keyword": "Given",
              "text": "user is on login page"
            },
            {
              "keyword": "When", 
              "text": "user enters valid credentials"
            },
            {
              "keyword": "Then",
              "text": "user should be redirected to dashboard"
            }
          ]
        },
        {
          "name": "Login with different user types",
          "type": "scenario-outline",
          "description": "Test login with various user types",
          "steps": [
            {
              "keyword": "Given",
              "text": "user is on login page"
            },
            {
              "keyword": "When",
              "text": "user enters <username> and <password>"
            },
            {
              "keyword": "Then", 
              "text": "user should see <result>"
            }
          ],
          "examples": {
            "headers": ["username", "password", "result"],
            "rows": [
              {
                "values": {
                  "values": ["admin", "admin123", "Dashboard"]
                }
              },
              {
                "values": {
                  "values": ["user", "user123", "Home Page"]
                }
              }
            ]
          }
        }
      ]
    }
  ]
}
```

## 📊 مدیریت Log ها

### تنظیمات پیش‌فرض
- **حداکثر اندازه فایل**: 5MB
- **تعداد backup**: 3 فایل  
- **مدت نگهداری**: 7 روز
- **فضای کل**: ~20MB

### Log Files
```
logs/
  azure_test_import.log       # فایل اصلی
  azure_test_import.log.1     # Backup 1
  azure_test_import.log.2     # Backup 2
  azure_test_import.log.3     # Backup 3
```

### مشاهده Log ها
```bash
# آخرین 100 خط
curl "http://localhost:5050/api/v1/logs/100"

# آخرین 50 خط  
curl "http://localhost:5050/api/v1/logs/50"
```

## 🧪 تست

### اجرای تست‌ها
```bash
pytest tests/ -v
```

### تست سریع API
```bash
# Health check
curl "http://localhost:5050/api/v1/health"

# Info endpoint
curl "http://localhost:5050/info"

# Debug version logic
curl "http://localhost:5050/api/v1/import/debug/version/TestProject/1.0.0"
```

## 🔧 Configuration Options

| Environment Variable | Default | توضیحات |
|---------------------|---------|---------|
| `AZURE_DEVOPS_ORG_URL` | `http://192.168.10.22:8080/tfs/RPKavoshDevOps` | URL سازمان Azure DevOps |
| `AZURE_DEVOPS_PROJECT` | `Test Process` | نام پروژه پیش‌فرض |
| `LOG_LEVEL` | `INFO` | سطح logging |
| `LOG_MAX_FILE_SIZE_MB` | `5` | حداکثر اندازه فایل log |
| `LOG_BACKUP_COUNT` | `3` | تعداد فایل‌های backup |
| `LOG_CLEANUP_DAYS` | `7` | مدت نگهداری log ها |

## 🛠️ Dependencies

```
fastapi==0.104.1          # Core framework
uvicorn[standard]==0.24.0 # ASGI server
pydantic==2.11.7          # Data validation
requests==2.31.0          # HTTP client
requests-ntlm>=1.1.0      # NTLM authentication
python-multipart==0.0.6   # File upload support
pytest==8.4.1             # Testing framework
httpx==0.28.1             # Async HTTP client for tests
python-dotenv==1.0.1      # Environment file support
```

## 🐛 Troubleshooting

### مشکلات رایج

#### 1. خطای 401 Unauthorized
```bash
# بررسی format token
# NTLM: "username:password"
# PAT: ":your_personal_access_token"
```

#### 2. خطای 404 Not Found Task
```bash
# بررسی task_id و استفاده از endpoint صحیح
curl "http://localhost:5050/api/v1/import/debug/tasks"
```

#### 3. خطای 500 Internal Server Error
```bash
# بررسی logs برای جزئیات بیشتر
curl "http://localhost:5050/api/v1/logs/100"
```

#### 4. مشکل connection به Azure DevOps
```bash
# تست connection manual
curl -X GET "http://localhost:5050/api/v1/health"
```

### Log Messages مهم

```
✅ Created NEW test plan for MAJOR version
🔄 Patch version change - Looking for existing plan to UPDATE
📝 Will update content of existing test plan with new test cases
⚠️  WARNING: All test cases went to the same suite!
```

## 📈 Performance Tips

1. **Async Processing**: همیشه از `/import/async` استفاده کنید
2. **Progress Monitoring**: status endpoint را منظم چک کنید
3. **Log Management**: environment variables را برای کنترل log ها تنظیم کنید
4. **Version Strategy**: از منطق versioning درست استفاده کنید

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For questions and support:
- 📧 Email: support@example.com
- 📖 Documentation: `http://localhost:5050/docs`
- 🐛 Issues: GitHub Issues