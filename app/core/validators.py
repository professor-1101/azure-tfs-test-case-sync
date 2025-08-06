import re
from typing import Optional
from fastapi import HTTPException


def validate_semantic_version(version: str) -> str:
    """
    Validate that the version string follows semantic versioning format.
    
    Args:
        version: Version string to validate
        
    Returns:
        The validated version string
        
    Raises:
        ValueError: If version doesn't follow semantic versioning format
    """
    # Semantic versioning pattern: major.minor.patch
    pattern = r'^\d+\.\d+\.\d+$'
    
    if not re.match(pattern, version):
        raise ValueError(
            f"Version '{version}' must follow semantic versioning format (e.g., '1.2.3', '2.0.0')"
        )
    
    # Parse version components
    try:
        major, minor, patch = map(int, version.split('.'))
        
        # Validate ranges (optional - you can adjust these)
        if major < 0 or minor < 0 or patch < 0:
            raise ValueError("Version components must be non-negative integers")
            
        if major > 999 or minor > 999 or patch > 999:
            raise ValueError("Version components must be less than 1000")
            
    except ValueError as e:
        raise ValueError(f"Invalid version format: {e}")
    
    return version


def validate_project_name(project_name: str) -> str:
    """
    Validate project name format.
    
    Args:
        project_name: Project name to validate
        
    Returns:
        The validated project name
        
    Raises:
        ValueError: If project name is invalid
    """
    if not project_name or not project_name.strip():
        raise ValueError("Project name cannot be empty")
    
    if len(project_name.strip()) < 1:
        raise ValueError("Project name must be at least 1 character long")
    
    if len(project_name.strip()) > 100:
        raise ValueError("Project name must be less than 100 characters")
    
    # Check for invalid characters (Azure DevOps restrictions)
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    for char in invalid_chars:
        if char in project_name:
            raise ValueError(f"Project name cannot contain character: '{char}'")
    
    return project_name.strip()


def validate_token_format(token: str) -> str:
    """
    Validate token format for authentication.
    
    Args:
        token: Token string to validate
        
    Returns:
        The validated token string
        
    Raises:
        ValueError: If token format is invalid
    """
    if not token or not token.strip():
        raise ValueError("Token cannot be empty")
    
    # Check if it's NTLM format (username:password)
    if ':' in token and not token.startswith(':'):
        # NTLM format
        username, password = token.split(':', 1)
        if not username.strip():
            raise ValueError("Username cannot be empty in NTLM format")
        if not password.strip():
            raise ValueError("Password cannot be empty in NTLM format")
    
    # Check if it's Basic Auth format (:PAT)
    elif token.startswith(':'):
        if len(token) < 2:
            raise ValueError("PAT token cannot be empty in Basic Auth format")
    
    else:
        # Assume it's a PAT without prefix
        if len(token.strip()) < 1:
            raise ValueError("Token cannot be empty")
    
    return token.strip()


def validate_content_structure(content: dict) -> dict:
    """
    Validate the structure of the content JSON.
    
    Args:
        content: Content dictionary to validate
        
    Returns:
        The validated content dictionary
        
    Raises:
        ValueError: If content structure is invalid
    """
    if not isinstance(content, dict):
        raise ValueError("Content must be a JSON object")
    
    if 'name' not in content:
        raise ValueError("Content must contain 'name' field")
    
    if 'features' not in content:
        raise ValueError("Content must contain 'features' field")
    
    if not isinstance(content['features'], list):
        raise ValueError("Features must be an array")
    
    if len(content['features']) == 0:
        raise ValueError("At least one feature must be provided")
    
    # Validate each feature
    for i, feature in enumerate(content['features']):
        if not isinstance(feature, dict):
            raise ValueError(f"Feature {i} must be an object")
        
        if 'name' not in feature:
            raise ValueError(f"Feature {i} must contain 'name' field")
        
        if 'scenarios' not in feature:
            raise ValueError(f"Feature {i} must contain 'scenarios' field")
        
        if not isinstance(feature['scenarios'], list):
            raise ValueError(f"Scenarios in feature {i} must be an array")
        
        if len(feature['scenarios']) == 0:
            raise ValueError(f"Feature {i} must contain at least one scenario")
        
        # Validate each scenario
        for j, scenario in enumerate(feature['scenarios']):
            if not isinstance(scenario, dict):
                raise ValueError(f"Scenario {j} in feature {i} must be an object")
            
            if 'name' not in scenario:
                raise ValueError(f"Scenario {j} in feature {i} must contain 'name' field")
            
            if 'steps' not in scenario:
                raise ValueError(f"Scenario {j} in feature {i} must contain 'steps' field")
            
            if not isinstance(scenario['steps'], list):
                raise ValueError(f"Steps in scenario {j} of feature {i} must be an array")
            
            if len(scenario['steps']) == 0:
                raise ValueError(f"Scenario {j} in feature {i} must contain at least one step")
            
            # Validate each step
            for k, step in enumerate(scenario['steps']):
                if not isinstance(step, dict):
                    raise ValueError(f"Step {k} in scenario {j} of feature {i} must be an object")
                
                if 'keyword' not in step:
                    raise ValueError(f"Step {k} in scenario {j} of feature {i} must contain 'keyword' field")
                
                if 'text' not in step:
                    raise ValueError(f"Step {k} in scenario {j} of feature {i} must contain 'text' field")
    
    return content 