from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class ErrorDetail(BaseModel):
    """Error detail for API responses."""
    
    scenario_title: str = Field(..., description="Title of the scenario that failed")
    error_message: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Type of error")


class ImportResponse(BaseModel):
    """Response model for import operations."""
    
    status: str = Field(..., description="Status of the operation")
    created: int = Field(..., description="Number of test cases created")
    errors: List[ErrorDetail] = Field(default_factory=list, description="List of errors encountered")
    test_plan_id: Optional[int] = Field(None, description="ID of the test plan used")
    test_suite_id: Optional[int] = Field(None, description="ID of the test suite used")
    all_suite_ids: List[int] = Field(default_factory=list, description="List of all suite IDs created")
    logs: List[str] = Field(default_factory=list, description="Relevant log messages for debugging")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "created": 7,
                "errors": [],
                "test_plan_id": 123,
                "test_suite_id": 456,
                "all_suite_ids": [456, 457, 458]
            }
        }


class AsyncImportResponse(BaseModel):
    task_id: str
    status: str
    message: str


class AsyncImportStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: Optional[int] = None
    result: Optional[ImportResponse] = None
    error: Optional[str] = None
    logs: List[str] = []


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    azure_devops_connected: bool = Field(..., description="Azure DevOps connection status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "azure_devops_connected": True
            }
        }


class TestPlanInfo(BaseModel):
    """Information about a test plan."""
    
    id: int = Field(..., description="Test plan ID")
    name: str = Field(..., description="Test plan name")
    description: Optional[str] = Field(None, description="Test plan description")
    root_suite_id: int = Field(..., description="Root suite ID")


class TestSuiteInfo(BaseModel):
    """Information about a test suite."""
    
    id: int = Field(..., description="Test suite ID")
    name: str = Field(..., description="Test suite name")
    parent_suite_id: Optional[int] = Field(None, description="Parent suite ID")


class TestCaseInfo(BaseModel):
    """Information about a test case."""
    
    id: int = Field(..., description="Test case ID")
    title: str = Field(..., description="Test case title")
    description: Optional[str] = Field(None, description="Test case description")
    has_parameters: bool = Field(..., description="Whether the test case has parameters") 