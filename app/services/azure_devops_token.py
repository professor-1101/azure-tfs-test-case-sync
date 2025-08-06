import urllib.parse
import requests
import re
from requests_ntlm import HttpNtlmAuth
from typing import Dict, Any, Optional, List
import time
from app.core.logging import get_logger, setup_logging
from app.core.exceptions import (
    AzureDevOpsException,
    TestCaseCreationException
)

logger = get_logger(__name__)

class AzureDevOpsTokenService:
    def __init__(self, org_url: str, project_name: str, token: str, api_version: str = "5.0"):
        # Setup logging first
        setup_logging()
        
        self.org_url = org_url.rstrip('/')
        self.project_name = project_name
        self.api_version = api_version
        self.session = requests.Session()
        self.session.timeout = (10, 60)

        if ':' in token:
            username, password = token.split(':', 1)
        else:
            username = ""
            password = token

        self.session.auth = HttpNtlmAuth(username, password)
        self.session.headers.update({
            "Content-Type": "application/json"
        })

        logger.info(f"Using NTLM authentication with username: {username}")
        logger.info(f"AzureDevOpsTokenService initialized for project: {project_name}")

    def _request(self, method: str, url: str, json_data: Optional[Dict[str, Any]] = None, 
                 content_type_json_patch: bool = False) -> Dict[str, Any]:
        headers = self.session.headers.copy()
        if content_type_json_patch:
            headers["Content-Type"] = "application/json-patch+json"

        logger.info(f"{method}: {url}")
        if json_data:
            logger.debug(f"Payload: {json_data}")

        response = None
        try:
            if method == "GET":
                response = self.session.get(url, headers=headers)
            elif method == "POST":
                response = self.session.post(url, json=json_data, headers=headers)
            elif method == "PATCH":
                response = self.session.patch(url, json=json_data, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            logger.info(f"Response Status: {response.status_code}")
            logger.debug(f"Response Body: {response.text}")

            if response.status_code >= 400:
                error_msg = f"{method} request to {url} failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    error_details = error_data.get("message", error_data.get("value", str(error_data)))
                    error_msg += f"\nDetails: {error_details}"
                except:
                    error_msg += f"\nResponse: {response.text[:500]}"
                logger.error(error_msg)
                # Log the full response body for debugging
                logger.error(f"Full response body: {response.text}")

            response.raise_for_status()
            return response.json() if response.content else {}

        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error: {e.response.status_code} - {e.response.reason}"
            try:
                error_data = e.response.json()
                error_details = error_data.get("message", error_data.get("value", str(error_data)))
                error_msg += f"\nDetails: {error_details}"
            except:
                error_msg += f"\nResponse: {e.response.text[:500]}"
            logger.error(error_msg)
            logger.error(f"Full response body: {e.response.text}")
            raise AzureDevOpsException(error_msg) from e
        except requests.exceptions.RequestException as e:
            error_msg = f"{method} request to {url} failed"
            if response:
                error_msg += f" with status {response.status_code}"
                try:
                    error_details = response.json()
                    error_msg += f": {error_details.get('message', str(error_details))}"
                except:
                    error_msg += f": {response.text[:500]}"
                logger.error(f"Full response body: {response.text}")
            logger.error(error_msg)
            raise AzureDevOpsException(error_msg) from e

    def check_connection(self) -> bool:
        try:
            # Use project-specific endpoint instead of general projects endpoint
            url = f"{self.org_url}/{urllib.parse.quote(self.project_name)}/_apis/test/plans?api-version={self.api_version}"
            self._request("GET", url)
            logger.info("✅ Connection to Azure DevOps successful")
            return True
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            return False

    def get_test_plan(self, plan_name: str) -> Optional[Dict[str, Any]]:
        try:
            url = f"{self.org_url}/{urllib.parse.quote(self.project_name)}/_apis/test/plans?api-version={self.api_version}"
            data = self._request("GET", url)
            
            logger.info(f"Searching for test plan: '{plan_name}'")
            logger.info(f"Available test plans: {[plan.get('name', '') for plan in data.get('value', [])]}")
            
            for plan in data.get("value", []):
                plan_name_from_api = plan.get("name", "")
                logger.info(f"Comparing: '{plan_name_from_api}' with '{plan_name}'")
                
                if plan_name_from_api.lower() == plan_name.lower():
                    logger.info(f"✅ Found test plan: {plan_name} (ID: {plan['id']})")
                    return plan
            
            logger.warning(f"❌ Test plan '{plan_name}' not found")
            return None
        except Exception as e:
            logger.error(f"Error getting test plan: {e}")
            return None

    def create_test_plan(self, plan_name: str) -> Dict[str, Any]:
        url = f"{self.org_url}/{urllib.parse.quote(self.project_name)}/_apis/test/plans?api-version={self.api_version}"
        payload = {
            "name": plan_name,
            "description": f"Test plan created by automation script - {plan_name}",
            "startDate": None,
            "endDate": None,
            "iteration": self.project_name,
            "areaPath": self.project_name
        }
        logger.info(f"Creating test plan: {plan_name}")
        return self._request("POST", url, json_data=payload)

    def get_or_create_test_plan(self, plan_name: str) -> Dict[str, Any]:
        plan = self.get_test_plan(plan_name)
        if plan:
            return plan

        logger.info(f"Test plan '{plan_name}' not found, trying to find any existing test plan")
        url = f"{self.org_url}/{urllib.parse.quote(self.project_name)}/_apis/test/plans?api-version={self.api_version}"
        try:
            data = self._request("GET", url)
            if data.get("value"):
                return data["value"][0]
        except Exception as e:
            logger.error(f"Error getting test plans: {e}")

        return self.create_test_plan(plan_name)

    def get_root_suite_id(self, plan_id: int) -> int:
        """Get the root suite ID for a test plan."""
        url = f"{self.org_url}/{urllib.parse.quote(self.project_name)}/_apis/test/plans/{plan_id}?api-version={self.api_version}"
        data = self._request("GET", url)
        root_suite_id = data.get("rootSuite", {}).get("id")
        if root_suite_id:
            logger.info(f"Root suite ID for plan {plan_id}: {root_suite_id}")
            return root_suite_id
        else:
            raise AzureDevOpsException(f"Could not find root suite for plan {plan_id}")

    def _normalize_suite_name(self, name: str) -> str:
        """Normalize suite name by removing version patterns, timestamps, and special characters."""
        if not name or not name.strip():
            return "unnamed_suite"
        
        # Remove version patterns (more comprehensive)
        name = re.sub(r'\s*-?\s*v?(ersion)?\s?\d+(\.\d+){0,2}(-[a-zA-Z0-9]+)?$', '', name, flags=re.IGNORECASE)
        
        # Remove timestamp patterns (e.g., _1754396042)
        name = re.sub(r'_\d{10,}$', '', name)
        
        # Remove or replace problematic characters
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        
        # Normalize whitespace
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Ensure minimum length
        if len(name) < 1:
            return "unnamed_suite"
        
        # Truncate if too long (Azure DevOps has limits)
        if len(name) > 200:
            name = name[:197] + "..."
        
        return name.lower()

    def _validate_suite_name(self, name: str) -> str:
        """Validate and clean suite name for Azure DevOps."""
        if not name or not name.strip():
            raise ValueError("Suite name cannot be empty")
        
        # Check for minimum length
        if len(name.strip()) < 1:
            raise ValueError("Suite name is too short")
        
        # Check for maximum length (Azure DevOps limit)
        if len(name) > 200:
            raise ValueError(f"Suite name is too long ({len(name)} characters, max 200)")
        
        # Check for problematic characters
        problematic_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        found_chars = [char for char in problematic_chars if char in name]
        if found_chars:
            logger.warning(f"Suite name contains problematic characters: {found_chars}")
            # Replace problematic characters
            for char in problematic_chars:
                name = name.replace(char, '_')
        
        return name.strip()

    def find_or_create_suite(self, plan_id: int, parent_suite_id: int, suite_name: str) -> int:
        # Validate and clean the suite name
        try:
            validated_suite_name = self._validate_suite_name(suite_name)
            logger.info(f"Validated suite name: '{suite_name}' -> '{validated_suite_name}'")
        except ValueError as e:
            logger.error(f"Invalid suite name '{suite_name}': {e}")
            # Use a fallback name
            validated_suite_name = f"suite_{int(time.time())}"
            logger.warning(f"Using fallback suite name: '{validated_suite_name}'")
        
        normalized_suite_name = self._normalize_suite_name(validated_suite_name)
        logger.info(f"Looking for suite: '{validated_suite_name}' (normalized: '{normalized_suite_name}') under parent {parent_suite_id}")

        # Check for existing suites under the parent suite
        url = f"{self.org_url}/{urllib.parse.quote(self.project_name)}/_apis/test/plans/{plan_id}/suites/{parent_suite_id}/suites?api-version={self.api_version}"
        try:
            data = self._request("GET", url)
            
            for suite in data.get("value", []):
                if self._normalize_suite_name(suite.get("name", "")) == normalized_suite_name:
                    logger.info(f"Found existing suite: {suite['id']} with name '{suite.get('name', '')}'")
                    return suite["id"]
        except AzureDevOpsException as e:
            logger.warning(f"Could not get existing suites under parent {parent_suite_id}: {e}")

        # Create new suite under the parent suite
        try:
            logger.info(f"Creating new suite: '{validated_suite_name}' under parent {parent_suite_id}")
            url = f"{self.org_url}/{urllib.parse.quote(self.project_name)}/_apis/test/plans/{plan_id}/suites/{parent_suite_id}/suites?api-version={self.api_version}"
            payload = {
                "name": validated_suite_name,
                "description": f"Test suite created by automation script - {validated_suite_name}",
                "suiteType": "StaticTestSuite"
            }
            data = self._request("POST", url, json_data=payload)
            
            # Log the full response for debugging
            logger.info(f"Suite creation response: {data}")
            
            # Check if response has the expected structure
            if not data:
                raise AzureDevOpsException(f"Empty response from suite creation for '{validated_suite_name}'")
            
            # Azure DevOps API returns nested structure: {'value': [{'id': ..., 'name': ...}], 'count': 1}
            if 'value' in data and data['value'] and len(data['value']) > 0:
                suite_id = data['value'][0]['id']
                logger.info(f"Successfully created suite: {suite_id} with name '{validated_suite_name}' under parent {parent_suite_id}")
                return suite_id
            elif 'id' in data:
                # Fallback for direct id in response
                suite_id = data['id']
                logger.info(f"Successfully created suite: {suite_id} with name '{validated_suite_name}' under parent {parent_suite_id}")
                return suite_id
            else:
                logger.error(f"Response missing 'id' field: {data}")
                raise AzureDevOpsException(f"Response missing 'id' field for suite '{validated_suite_name}': {data}")
            logger.info(f"Successfully created suite: {suite_id} with name '{validated_suite_name}' under parent {parent_suite_id}")
            return suite_id
        except AzureDevOpsException as e:
            logger.error(f"Failed to create suite '{validated_suite_name}' under parent {parent_suite_id}: {e}")
            # Never fall back to parent suite - always raise the exception
            raise e

    def create_test_case(self, title: str, description: str = "Created by automation script") -> int:
        response = None
        try:
            url = f"{self.org_url}/{urllib.parse.quote(self.project_name)}/_apis/wit/workitems/$Test%20Case?api-version={self.api_version}"
            payload = [
                {"op": "add", "path": "/fields/System.Title", "value": title},
                {"op": "add", "path": "/fields/System.Description", "value": description}
            ]
            headers = {"Content-Type": "application/json-patch+json"}
            response = self.session.post(url, json=payload, headers=headers)
            logger.info(f"Create test case response status: {response.status_code}")
            response.raise_for_status()
            return response.json()["id"]
        except requests.exceptions.HTTPError as e:
            error_msg = f"Failed to create test case '{title}': {e.response.status_code} - {e.response.reason}"
            try:
                error_data = e.response.json()
                error_details = error_data.get("message", error_data.get("value", str(error_data)))
                error_msg += f"\nDetails: {error_details}"
            except:
                error_msg += f"\nResponse: {e.response.text[:500]}"
            logger.error(error_msg)
            logger.error(f"Full response body: {e.response.text}")
            raise TestCaseCreationException(error_msg) from e
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to create test case '{title}'"
            if response:
                error_msg += f": {response.status_code} - {response.text[:500]}"
                logger.error(f"Full response body: {response.text}")
            logger.error(error_msg)
            raise TestCaseCreationException(error_msg) from e

    def update_test_case_fields(self, tc_id: int, description: str, xml_steps: str, local_params_xml: Optional[str] = None) -> None:
        url = f"{self.org_url}/{urllib.parse.quote(self.project_name)}/_apis/wit/workitems/{tc_id}?api-version={self.api_version}"
        payload = [
            {"op": "add", "path": "/fields/System.Description", "value": description},
            {"op": "add", "path": "/fields/Microsoft.VSTS.TCM.Steps", "value": xml_steps}
        ]
        if local_params_xml:
            payload.append({
                "op": "add",
                "path": "/fields/Microsoft.VSTS.TCM.LocalDataSource",
                "value": local_params_xml
            })
        self._request("PATCH", url, json_data=payload, content_type_json_patch=True)

    def add_tc_to_suite(self, plan_id: int, suite_id: int, tc_id: int) -> None:
        url = f"{self.org_url}/{urllib.parse.quote(self.project_name)}/_apis/test/plans/{plan_id}/suites/{suite_id}/testcases/{tc_id}?api-version={self.api_version}"
        logger.info(f"Adding test case {tc_id} to suite {suite_id}")
        self._request("POST", url)

    def get_all_test_plans(self, project_name: str) -> List[Dict[str, Any]]:
        """Get all test plans for a project."""
        try:
            url = f"{self.org_url}/{urllib.parse.quote(project_name)}/_apis/test/plans?api-version={self.api_version}"
            logger.info(f"Getting all test plans for project: {project_name}")
            
            # _request returns Dict directly, not Response object
            data = self._request("GET", url)
            plans = data.get('value', [])
            
            logger.info(f"Successfully found {len(plans)} test plans for project {project_name}")
            
            # Log plan names for debugging
            for plan in plans:
                logger.info(f"Test plan found: {plan.get('name', 'UNNAMED')} (ID: {plan.get('id', 'NO_ID')})")
            
            return plans
                
        except Exception as e:
            logger.error(f"Error getting test plans for project {project_name}: {e}")
            return []

    def delete_test_plan(self, plan_id: int) -> bool:
        """Delete a test plan."""
        try:
            url = f"{self.org_url}/{urllib.parse.quote(self.project_name)}/_apis/test/plans/{plan_id}?api-version={self.api_version}"
            
            logger.info(f"🗑️ Deleting test plan: {plan_id}")
            
            # Use DELETE method 
            response = self.session.delete(url, headers=self.session.headers)
            response.raise_for_status()
            
            logger.info(f"✅ Successfully deleted test plan: {plan_id}")
            return True
                
        except Exception as e:
            logger.error(f"❌ Error deleting test plan {plan_id}: {e}")
            return False
