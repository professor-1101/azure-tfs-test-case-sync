import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json

from main import app
from app.schemas.responses import ImportResponse, HealthResponse

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    @patch('app.api.v1.endpoints.check_azure_devops_connection')
    def test_health_check_success(self, mock_check_connection):
        """Test health check when Azure DevOps is connected."""
        mock_check_connection.return_value = True
        
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert data["azure_devops_connected"] is True
    
    @patch('app.api.v1.endpoints.check_azure_devops_connection')
    def test_health_check_failure(self, mock_check_connection):
        """Test health check when Azure DevOps is not connected."""
        mock_check_connection.return_value = False
        
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["azure_devops_connected"] is False


class TestJsonImportEndpoint:
    """Test JSON import endpoint."""
    
    @patch('app.api.v1.endpoints.get_test_plan')
    @patch('app.api.v1.endpoints.find_or_create_suite')
    @patch('app.api.v1.endpoints.create_test_case')
    @patch('app.api.v1.endpoints.update_test_case_fields')
    @patch('app.api.v1.endpoints.add_tc_to_suite')
    def test_import_json_success(self, mock_add_to_suite, mock_update_fields, 
                                mock_create_case, mock_find_suite, mock_get_plan):
        """Test successful JSON import."""
        # Mock Azure DevOps responses
        mock_get_plan.return_value = {"id": 123, "rootSuite": {"id": 456}}
        mock_find_suite.return_value = 789
        mock_create_case.return_value = 999
        mock_update_fields.return_value = None
        mock_add_to_suite.return_value = None
        
        # Test data
        test_data = {
            "content": {
                "name": "Test Feature",
                "features": [
                    {
                        "name": "Test Feature",
                        "description": "Test description",
                        "scenarios": [
                            {
                                "name": "Test Scenario",
                                "type": "scenario",
                                "steps": [
                                    {"keyword": "وقتی", "text": "user does something"}
                                ]
                            }
                        ]
                    }
                ]
            },
            "test_plan_name": "Test Plan",
            "test_suite_name": "Test Suite"
        }
        
        response = client.post("/api/v1/import/json", json=test_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert data["created"] == 1
        assert len(data["errors"]) == 0
        assert data["test_plan_id"] == 123
        assert data["test_suite_id"] == 789
    
    def test_import_json_invalid_data(self):
        """Test JSON import with invalid data."""
        test_data = {
            "content": {
                "invalid": "data"
            }
        }
        
        response = client.post("/api/v1/import/json", json=test_data)
        assert response.status_code == 200  # Should still process but with no scenarios
    
    @patch('app.api.v1.endpoints.get_test_plan')
    def test_import_json_test_plan_not_found(self, mock_get_plan):
        """Test JSON import when test plan is not found."""
        mock_get_plan.return_value = None
        
        test_data = {
            "content": {
                "name": "Test Feature",
                "features": []
            },
            "test_plan_name": "Non-existent Plan"
        }
        
        response = client.post("/api/v1/import/json", json=test_data)
        assert response.status_code == 404


class TestFileImportEndpoint:
    """Test file import endpoint."""
    
    @patch('app.api.v1.endpoints.get_test_plan')
    @patch('app.api.v1.endpoints.find_or_create_suite')
    @patch('app.api.v1.endpoints.create_test_case')
    @patch('app.api.v1.endpoints.update_test_case_fields')
    @patch('app.api.v1.endpoints.add_tc_to_suite')
    def test_import_file_success(self, mock_add_to_suite, mock_update_fields, 
                                mock_create_case, mock_find_suite, mock_get_plan):
        """Test successful file import."""
        # Mock Azure DevOps responses
        mock_get_plan.return_value = {"id": 123, "rootSuite": {"id": 456}}
        mock_find_suite.return_value = 789
        mock_create_case.return_value = 999
        mock_update_fields.return_value = None
        mock_add_to_suite.return_value = None
        
        # Create test JSON file content
        test_content = {
            "name": "Test Feature",
            "features": [
                {
                    "name": "Test Feature",
                    "scenarios": [
                        {
                            "name": "Test Scenario",
                            "type": "scenario",
                            "steps": [
                                {"keyword": "وقتی", "text": "user does something"}
                            ]
                        }
                    ]
                }
            ]
        }
        
        # Create file upload
        files = {"file": ("test.json", json.dumps(test_content), "application/json")}
        data = {"test_plan_name": "Test Plan", "test_suite_name": "Test Suite"}
        
        response = client.post("/api/v1/import/file", files=files, data=data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert data["created"] == 1
    
    def test_import_file_invalid_format(self):
        """Test file import with invalid file format."""
        files = {"file": ("test.txt", "invalid content", "text/plain")}
        
        response = client.post("/api/v1/import/file", files=files)
        assert response.status_code == 400
        assert "Only JSON files are supported" in response.json()["detail"]
    
    def test_import_file_invalid_json(self):
        """Test file import with invalid JSON content."""
        files = {"file": ("test.json", "invalid json content", "application/json")}
        
        response = client.post("/api/v1/import/file", files=files)
        assert response.status_code == 400
        assert "Invalid JSON file" in response.json()["detail"]


class TestRootEndpoints:
    """Test root endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "health" in data
    
    def test_info_endpoint(self):
        """Test info endpoint."""
        response = client.get("/info")
        assert response.status_code == 200
        
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "description" in data
        assert "azure_devops" in data
        assert "endpoints" in data 