from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from enum import Enum
from app.core.validators import validate_semantic_version, validate_project_name, validate_token_format, validate_content_structure


class ImportType(str, Enum):
    """Type of import - file or text."""
    FILE = "file"
    TEXT = "text"


class GherkinImportRequest(BaseModel):
    """Request model for importing Gherkin content."""
    
    import_type: ImportType = Field(..., description="Type of import - file or text")
    content: Optional[str] = Field(None, description="Gherkin text content (when import_type is 'text')")
    test_plan_name: Optional[str] = Field(None, description="Override default test plan name")
    test_suite_name: Optional[str] = Field(None, description="Override default test suite name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "import_type": "text",
                "content": "Feature: Login\n  Scenario: Successful login\n    When user enters valid credentials\n    Then user should be logged in",
                "test_plan_name": "My Test Plan",
                "test_suite_name": "Login Tests"
            }
        }


class JsonImportRequest(BaseModel):
    """Request model for importing JSON content."""
    
    content: Dict[str, Any] = Field(..., description="JSON content with features and scenarios")
    test_plan_name: Optional[str] = Field(None, description="Override default test plan name")
    test_suite_name: Optional[str] = Field(None, description="Override default test suite name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": {
                    "name": "پست بانک",
                    "features": [
                        {
                            "name": "صفحه لاگین",
                            "scenarios": [
                                {
                                    "name": "ورود موفق کاربر",
                                    "steps": [
                                        {"keyword": "وقتی", "text": "کاربر فیلد \"نام کاربری\" را با <نام کاربری> وارد می‌کند"}
                                    ]
                                }
                            ]
                        }
                    ]
                },
                "test_plan_name": "تست کارتال",
                "test_suite_name": "لاگین"
            }
        }


class VersionedImportRequest(BaseModel):
    """Request model for versioned import with project name, token, and version."""
    
    project_name: str = Field(
        ..., 
        description="Name of the Azure DevOps project (e.g., 'Test Process')",
        example="Test Process"
    )
    token: str = Field(
        ..., 
        description="Azure DevOps authentication token in format 'username:password' for NTLM or ':PAT' for Basic Auth",
        example="RPK\\ASadeghianAzar:iLAus1101"
    )
    version: str = Field(
        ..., 
        description="Version string in semantic versioning format (e.g., '1.2.3', '2.0.0'). This is REQUIRED and will be used in test plan naming.",
        example="2.0.0",
        min_length=1,
        pattern="^\\d+\\.\\d+\\.\\d+$"
    )
    content: Dict[str, Any] = Field(
        ..., 
        description="JSON content with features and scenarios in Gherkin format"
    )

    @validator('project_name')
    def validate_project_name_field(cls, v):
        return validate_project_name(v)

    @validator('token')
    def validate_token_field(cls, v):
        return validate_token_format(v)

    @validator('version')
    def validate_version_field(cls, v):
        return validate_semantic_version(v)

    @validator('content')
    def validate_content_field(cls, v):
        return validate_content_structure(v)

    class Config:
        json_schema_extra = {
            "example": {
                "project_name": "Test Process",
                "token": "RPK\\ASadeghianAzar:iLAus1101",
                "version": "2.0.0",
                "content": {
                    "name": "تست ورژن جدید",
                    "features": [
                        {
                            "name": "صفحه لاگین",
                            "scenarios": [
                                {
                                    "name": "ورود موفق کاربر",
                                    "steps": [
                                        {"keyword": "وقتی", "text": "کاربر فیلد \"نام کاربری\" را با <نام کاربری> وارد می‌کند"},
                                        {"keyword": "و", "text": "کاربر فیلد \"رمز عبور\" را با <رمز عبور> وارد می‌کند"},
                                        {"keyword": "آنگاه", "text": "کاربر وارد سیستم می‌شود"}
                                    ],
                                    "outlines": [
                                        {"نام کاربری": "admin", "رمز عبور": "admin123"},
                                        {"نام کاربری": "user", "رمز عبور": "user123"}
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        }