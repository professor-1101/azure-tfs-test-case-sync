import re
from typing import Tuple
from app.core.logging import get_logger

logger = get_logger(__name__)

def parse_version(version_string: str) -> Tuple[int, int, int]:
    """Parse version string and return major, minor, patch components."""
    clean_version = version_string.lstrip('v')
    pattern = r'^(\d+)\.(\d+)\.(\d+)$'
    match = re.match(pattern, clean_version)
    if not match:
        raise ValueError(f'Invalid version format: {version_string}. Expected format: X.Y.Z')
    major, minor, patch = map(int, match.groups())
    return major, minor, patch

def compare_versions(old_version: str, new_version: str) -> str:
    """
    Compares two version strings and returns the change type.
    
    Logic:
    - If major changed → 'major' (always create new suite)
    - If minor changed → 'minor' (always create new suite)  
    - If only patch changed → 'patch' (update existing if found, create new if not)
    - If versions are equal → 'same' (no action needed)
    
    Args:
        old_version: Previous version string (e.g., "3.0.1")
        new_version: New version string (e.g., "3.0.3")
    
    Returns:
        str: One of 'major', 'minor', 'patch', 'same'
    """
    try:
        old_major, old_minor, old_patch = parse_version(old_version)
        new_major, new_minor, new_patch = parse_version(new_version)
        
        logger.info(f"Comparing versions: {old_version} -> {new_version}")
        logger.info(f"Old: major={old_major}, minor={old_minor}, patch={old_patch}")
        logger.info(f"New: major={new_major}, minor={new_minor}, patch={new_patch}")
        
        # Check if versions are equal
        if old_major == new_major and old_minor == new_minor and old_patch == new_patch:
            logger.info(f"Version {new_version} is SAME as {old_version}")
            return 'same'
        
        # Check if major changed
        if new_major != old_major:
            logger.info(f"Version {new_version} is MAJOR update from {old_version}")
            return 'major'
        
        # Check if minor changed
        if new_minor != old_minor:
            logger.info(f"Version {new_version} is MINOR update from {old_version}")
            return 'minor'
        
        # Only patch changed
        if new_patch != old_patch:
            logger.info(f"Version {new_version} is PATCH update from {old_version}")
            return 'patch'
        
        # This should never happen, but just in case
        logger.warning(f"Unexpected version comparison: {old_version} -> {new_version}")
        return 'same'
            
    except ValueError as e:
        logger.error(f'Error parsing version: {e}')
        raise

def generate_test_suite_name(project_name: str, version: str, version_type: str) -> str:
    """
    Generate test suite name based on version type.
    
    Args:
        project_name: Name of the project
        version: Version string
        version_type: One of 'major', 'minor', 'patch', 'same'
    
    Returns:
        str: Generated suite name
    """
    if version_type == 'patch':
        return f'{project_name} v{version}'
    else:
        return f'{project_name} v{version} ({version_type})'

def should_create_new_plan(version_type: str) -> bool:
    """
    Determine if a new test plan should be created based on version type.
    
    Logic based on user requirements:
    - Major: همیشه تست پلن جدید ساخته می‌شود
    - Minor: همیشه تست پلن جدید ساخته می‌شود  
    - Patch: اگر test suite وجود داشت، فقط نام آن به‌روزرسانی می‌شود
    - Same: محتوای تست پلن موجود به‌روزرسانی می‌شود
    
    Args:
        version_type: One of 'major', 'minor', 'patch', 'same'
    
    Returns:
        bool: True if new test plan should be created, False otherwise
    """
    return version_type in ['major', 'minor']

def should_update_existing(version_type: str) -> bool:
    """
    Determine if existing test plan should be updated based on version type.
    
    Args:
        version_type: One of 'major', 'minor', 'patch', 'same'
    
    Returns:
        bool: True if existing should be updated, False otherwise
    """
    return version_type in ['patch', 'same']
