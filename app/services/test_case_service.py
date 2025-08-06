"""Service for handling test case import operations."""

from typing import List, Dict, Any, Tuple, Optional
from app.services.azure_devops_token import AzureDevOpsTokenService
from app.parsers.json_parser import parse_json_content
from app.parsers.gherkin_parser import expand_outlines
from app.parsers.xml_formatter import format_steps_xml, format_local_parameters_xml
from app.core.version_utils import parse_version, compare_versions, generate_test_suite_name, should_create_new_plan, should_update_existing
from app.core.logging import get_logger, setup_logging
from app.schemas.responses import ImportResponse, ErrorDetail
from app.core.exceptions import TestSuiteCreationException

logger = get_logger(__name__)


class TestCaseService:
    """Service for importing test cases to Azure DevOps."""

    def __init__(self, azure_service: AzureDevOpsTokenService):
        # Setup logging first
        setup_logging()
        
        self.azure_service = azure_service

    def import_test_cases(
        self,
        json_data: Dict[str, Any],
        project_name: str,
        version: str
    ) -> ImportResponse:
        """Import test cases with version management."""
        major, minor, patch = parse_version(version)
        
        # Find the latest existing version to compare with
        # Special handling: exclude the current version from comparison to avoid "same" detection
        latest_version = self._find_latest_version_excluding(project_name, version)
        if latest_version:
            old_version = latest_version
            logger.info(f"Found latest version (excluding current): {latest_version}")
        else:
            old_version = "0.0.0"  # Default starting version
            logger.info(f"No existing version found, using default: {old_version}")
        
        version_type = compare_versions(old_version, version)
        logger.info(f"📊 Version comparison: {old_version} -> {version} = {version_type}")

        plan_id, root_suite_id = self._get_or_create_test_plan(project_name, version, version_type)
        created_count = 0
        errors = []
        all_suite_ids = []

        features = json_data.get("features", [])
        if not features:
            features = [{"name": json_data.get("name", "Default Feature"), "scenarios": []}]

        logger.info(f"Found {len(features)} features to process")

        for feature_idx, feature in enumerate(features, start=1):
            feature_name = feature.get("name", f"Feature {feature_idx}")
            logger.info(f"Processing feature {feature_idx}/{len(features)}: {feature_name}")

            try:
                feature_suite_id = self._create_feature_suite(plan_id, root_suite_id, feature_name, version, version_type)
                logger.info(f"Created feature suite ID: {feature_suite_id}")
                all_suite_ids.append(feature_suite_id)
            except Exception as e:
                logger.error(f"Failed to create suite for feature '{feature_name}': {e}")
                errors.append(ErrorDetail(
                    scenario_title=f"Feature: {feature_name}",
                    error_message=f"Could not create suite: {str(e)}",
                    error_type=type(e).__name__
                ))
                # Skip this feature entirely - don't add test cases to root suite
                continue

            feature_scenarios = feature.get("scenarios", [])
            logger.info(f"Found {len(feature_scenarios)} scenarios in feature '{feature_name}'")

            for scenario_idx, scenario in enumerate(feature_scenarios, start=1):
                logger.info(f"Processing scenario {scenario_idx}/{len(feature_scenarios)}: {scenario.get('name', 'Unknown')}")

                try:
                    test_case_ids = self._create_test_case_from_scenario(
                        scenario,
                        plan_id,
                        feature_suite_id,
                        version
                    )

                    created_count += len(test_case_ids)
                    logger.info(f"Successfully created test case(s) for: {scenario.get('name', 'Unknown')}")

                except Exception as e:
                    logger.error(f"Error processing scenario '{scenario.get('name', 'Unknown')}': {str(e)}")
                    errors.append(ErrorDetail(
                        scenario_title=f"{feature_name} - {scenario.get('name', 'Unknown')}",
                        error_message=str(e),
                        error_type=type(e).__name__
                    ))

        logger.info(f"Import completed: {created_count} test cases created, {len(errors)} errors")
        logger.info(f"Created {len(all_suite_ids)} different suites: {all_suite_ids}")

        # Check if all test cases went to the same suite
        if len(all_suite_ids) == 1:
            logger.warning("⚠️ WARNING: All test cases went to the same suite!")
        else:
            logger.info(f"✅ Test cases distributed across {len(all_suite_ids)} different suites")

        # Determine the main test_suite_id for response
        # If we have multiple suites, use the first one as primary
        # If all failed, use root_suite_id
        main_suite_id = all_suite_ids[0] if all_suite_ids else root_suite_id
        
        logger.info(f"📊 Final Summary:")
        logger.info(f"   - Test Plan ID: {plan_id}")
        logger.info(f"   - Root Suite ID: {root_suite_id}")
        logger.info(f"   - Created Suites: {all_suite_ids}")
        logger.info(f"   - Main Suite ID (for response): {main_suite_id}")

        # Capture relevant logs for debugging
        logs = [
            f"Import completed: {created_count} test cases created, {len(errors)} errors",
            f"Created {len(all_suite_ids)} different suites: {all_suite_ids}",
            f"Test Plan ID: {plan_id}",
            f"Root Suite ID: {root_suite_id}",
            f"Main Suite ID: {main_suite_id}"
        ]
        
        if len(all_suite_ids) == 1:
            logs.append("⚠️ WARNING: All test cases went to the same suite!")
        else:
            logs.append(f"✅ Test cases distributed across {len(all_suite_ids)} different suites")

        return ImportResponse(
            status="success" if len(errors) == 0 else "partial_success",
            created=created_count,
            errors=errors,
            test_plan_id=plan_id,
            test_suite_id=main_suite_id,
            all_suite_ids=all_suite_ids,
            logs=logs
        )

    def _find_latest_version_excluding(self, project_name: str, exclude_version: str) -> Optional[str]:
        """
        Find the latest existing version for the project, excluding a specific version.
        This prevents the "same" version issue when the target version already exists.
        
        Args:
            project_name: Name of the project
            exclude_version: Version to exclude from search
            
        Returns:
            Optional[str]: Latest version string or None if no versions found
        """
        try:
            # Get all test plans for the project
            all_plans = self.azure_service.get_all_test_plans(project_name)
            logger.info(f"Found {len(all_plans)} test plans for project {project_name}")
            
            # Extract versions from plan names, excluding the target version
            versions = []
            prefix = f"{project_name} Test Plan v"
            logger.info(f"Looking for plans with prefix: '{prefix}', excluding version: {exclude_version}")
            
            for plan in all_plans:
                plan_name = plan.get('name', '')
                if prefix in plan_name:
                    version_part = plan_name.replace(prefix, "")
                    logger.debug(f"Extracted version part: '{version_part}' from plan: '{plan_name}'")
                    
                    # Skip the version we want to exclude
                    if version_part == exclude_version:
                        logger.info(f"Skipping current version: {version_part}")
                        continue
                        
                    try:
                        # Validate version format
                        parse_version(version_part)
                        versions.append(version_part)
                        logger.info(f"Valid version found: {version_part}")
                    except ValueError as e:
                        # Skip invalid versions
                        logger.warning(f"Invalid version format: {version_part}, error: {e}")
                        continue
            
            if not versions:
                logger.info(f"No valid versions found for project {project_name} (excluding {exclude_version})")
                return None
            
            # Sort versions and get the latest
            versions.sort(key=lambda v: parse_version(v), reverse=True)
            latest_version = versions[0]
            logger.info(f"Latest version found (excluding {exclude_version}): {latest_version}")
            return latest_version
            
        except Exception as e:
            logger.error(f"Error finding latest version (excluding {exclude_version}): {e}")
            return None

    def _find_latest_version(self, project_name: str) -> Optional[str]:
        """
        Find the latest existing version for the project.
        
        Args:
            project_name: Name of the project
            
        Returns:
            Optional[str]: Latest version string or None if no versions found
        """
        try:
            # Get all test plans for the project
            all_plans = self.azure_service.get_all_test_plans(project_name)
            logger.info(f"Found {len(all_plans)} test plans for project {project_name}")
            
            # Log all plan names for debugging
            for plan in all_plans:
                logger.info(f"Plan found: {plan.get('name', 'UNNAMED')}")
            
            # Extract versions from plan names
            versions = []
            prefix = f"{project_name} Test Plan v"
            logger.info(f"Looking for plans with prefix: '{prefix}'")
            
            for plan in all_plans:
                plan_name = plan.get('name', '')
                if prefix in plan_name:
                    version_part = plan_name.replace(prefix, "")
                    logger.info(f"Extracted version part: '{version_part}' from plan: '{plan_name}'")
                    try:
                        # Validate version format
                        parse_version(version_part)
                        versions.append(version_part)
                        logger.info(f"Valid version found: {version_part}")
                    except ValueError as e:
                        # Skip invalid versions
                        logger.warning(f"Invalid version format: {version_part}, error: {e}")
                        continue
                else:
                    logger.debug(f"Plan name doesn't match prefix: '{plan_name}'")
            
            if not versions:
                logger.info(f"No valid versions found for project {project_name}")
                return None
            
            # Sort versions and get the latest
            versions.sort(key=lambda v: parse_version(v), reverse=True)
            latest_version = versions[0]
            logger.info(f"Latest version found: {latest_version}")
            return latest_version
            
        except Exception as e:
            logger.error(f"Error finding latest version: {e}")
            return None

    def _get_or_create_test_plan(
        self,
        project_name: str,
        version: str,
        version_type: str
    ) -> Tuple[int, int]:
        plan_name = f"{project_name} Test Plan v{version}"
        logger.info(f"🔄 Version Management Logic: {version_type} version detected")
        logger.info(f"📋 Target plan name: {plan_name}")

        if version_type == 'major':
            # Major: همیشه تست پلن جدید ساخته می‌شود
            logger.info(f"🆕 Major version change - Creating NEW test plan: {plan_name}")
            plan = self.azure_service.create_test_plan(plan_name)
            logger.info(f"✅ Created NEW test plan for MAJOR version: {plan_name} (ID: {plan['id']})")
            
        elif version_type == 'minor':
            # Minor: همیشه تست پلن جدید ساخته می‌شود  
            logger.info(f"🆕 Minor version change - Creating NEW test plan: {plan_name}")
            plan = self.azure_service.create_test_plan(plan_name)
            logger.info(f"✅ Created NEW test plan for MINOR version: {plan_name} (ID: {plan['id']})")
            
        elif version_type == 'patch':
            # Patch: پلن قدیمی پاک کن، جدید بساز با version جدید
            logger.info(f"🔄 Patch version change - DELETE old plan and CREATE new one...")
            
            # Parse current version
            major, minor, patch = parse_version(version)
            
            # Find existing plan with same major.minor
            existing_plan = self._find_similar_test_plan(project_name, major, minor)
            
            if existing_plan:
                logger.info(f"🗑️ Found existing plan for PATCH - DELETING: {existing_plan['name']} (ID: {existing_plan['id']})")
                
                # Delete the old plan
                delete_success = self.azure_service.delete_test_plan(existing_plan['id'])
                
                if delete_success:
                    logger.info(f"✅ Successfully deleted old plan: {existing_plan['name']}")
                else:
                    logger.warning(f"⚠️ Failed to delete old plan, but continuing...")
            
            # Always create new plan with current version
            logger.info(f"🆕 Creating NEW test plan for PATCH: {plan_name}")
            plan = self.azure_service.create_test_plan(plan_name)
            logger.info(f"✅ Created NEW test plan for PATCH: {plan_name} (ID: {plan['id']})")
                
        else:  # version_type == 'same'
            # Same: پلن قدیمی پاک کن، جدید بساز (محتوا اپدیت)
            logger.info(f"🔄 Same version detected - DELETE old plan and CREATE fresh one...")
            
            existing_plan = self.azure_service.get_test_plan(plan_name)
            if existing_plan:
                logger.info(f"🗑️ Found existing plan for SAME version - DELETING: {plan_name} (ID: {existing_plan['id']})")
                
                # Delete the old plan
                delete_success = self.azure_service.delete_test_plan(existing_plan['id'])
                
                if delete_success:
                    logger.info(f"✅ Successfully deleted old plan: {plan_name}")
                else:
                    logger.warning(f"⚠️ Failed to delete old plan, but continuing...")
            
            # Always create fresh plan
            logger.info(f"🆕 Creating FRESH test plan for SAME version: {plan_name}")
            plan = self.azure_service.create_test_plan(plan_name)
            logger.info(f"✅ Created FRESH test plan for SAME version: {plan_name} (ID: {plan['id']})")

        logger.info(f"📊 Final result: Using test plan ID {plan['id']} with root suite ID {plan['rootSuite']['id']}")
        return plan["id"], plan["rootSuite"]["id"]

    def _find_similar_test_plan(self, project_name: str, major: int, minor: int) -> Optional[Dict[str, Any]]:
        """
        Find existing test plan with same major.minor version.
        
        Args:
            project_name: Name of the project
            major: Major version number
            minor: Minor version number
            
        Returns:
            Optional[Dict]: Test plan info or None if not found
        """
        try:
            # Get all test plans for the project
            all_plans = self.azure_service.get_all_test_plans(project_name)
            logger.info(f"Looking for similar test plans with major.minor: {major}.{minor}")
            logger.info(f"Total plans found: {len(all_plans)}")
            
            # Find plans with same major.minor
            similar_plans = []
            for plan in all_plans:
                plan_name = plan.get('name', '')
                logger.debug(f"Checking plan: {plan_name}")
                
                if f"{project_name} Test Plan v" in plan_name:
                    version_part = plan_name.replace(f"{project_name} Test Plan v", "")
                    try:
                        plan_major, plan_minor, plan_patch = parse_version(version_part)
                        logger.debug(f"Parsed version: {plan_major}.{plan_minor}.{plan_patch}")
                        
                        if plan_major == major and plan_minor == minor:
                            similar_plans.append((plan, plan_patch))
                            logger.debug(f"Found similar plan: {plan_name} (patch: {plan_patch})")
                    except ValueError as e:
                        logger.debug(f"Invalid version format in plan name: {plan_name}, error: {e}")
                        continue
            
            if similar_plans:
                # Sort by patch version (latest first) and return the most recent
                similar_plans.sort(key=lambda x: x[1], reverse=True)
                latest_plan, latest_patch = similar_plans[0]
                logger.info(f"✅ Found similar test plan: {latest_plan['name']} (patch: {latest_patch})")
                return latest_plan
            
            logger.info(f"❌ No similar test plan found for major.minor: {major}.{minor}")
            return None
            
        except Exception as e:
            logger.error(f"Error finding similar test plan: {e}")
            return None

    def _create_test_case_from_scenario(
        self,
        scenario: Dict[str, Any],
        plan_id: int,
        suite_id: int,
        version: str
    ) -> List[int]:
        scenario_name = scenario.get("name", "Unknown Scenario")
        scenario_description = scenario.get("description", "")

        steps = [f"{step.get('keyword', '')} {step.get('text', '')}" for step in scenario.get("steps", [])]

        if scenario.get("type") == "scenario-outline":
            examples = scenario.get("examples", {})
            headers = examples.get("headers", [])
            rows = examples.get("rows", [])

            # Create a single test case for scenario outline
            tc_id = self.azure_service.create_test_case(
                scenario_name,
                description=scenario_description or f"Created by automation script - Version {version}"
            )

            # Build the examples table as HTML for better display
            examples_table = "\n\n<h3>Examples Table:</h3>\n<table border='1' style='border-collapse: collapse; width: 100%;'>\n"
            if headers:
                # Create header row
                examples_table += "<tr style='background-color: #f2f2f2;'>\n"
                for header in headers:
                    examples_table += f"<th style='padding: 8px; text-align: left; border: 1px solid #ddd;'>{header}</th>\n"
                examples_table += "</tr>\n"
                
                # Create data rows
                for row in rows:
                    row_values = row.get("values", {}).get("values", [])
                    examples_table += "<tr>\n"
                    for val in row_values:
                        examples_table += f"<td style='padding: 8px; text-align: left; border: 1px solid #ddd;'>{str(val)}</td>\n"
                    examples_table += "</tr>\n"
            
            examples_table += "</table>\n"

            # Create enhanced description with examples table
            enhanced_description = f"{scenario_description or 'Created by automation script'}\n{examples_table}"
            
            # Keep steps as they are - don't replace variables
            # Variables like <کد ساختار سازمانی> should remain as placeholders
            expanded_steps = steps.copy()
            logger.info(f"Keeping steps with variables as placeholders: {expanded_steps}")

            xml_steps = format_steps_xml(expanded_steps)

            self.azure_service.update_test_case_fields(
                tc_id,
                enhanced_description,
                xml_steps
            )
            self.azure_service.add_tc_to_suite(plan_id, suite_id, tc_id)
            return [tc_id]

        else:
            tc_id = self.azure_service.create_test_case(
                scenario_name,
                description=scenario_description or f"Created by automation script - Version {version}"
            )
            xml_steps = format_steps_xml(steps)
            self.azure_service.update_test_case_fields(
                tc_id,
                scenario_description or f"Created by automation script - Version {version}",
                xml_steps
            )
            self.azure_service.add_tc_to_suite(plan_id, suite_id, tc_id)
            return [tc_id]

    def _create_feature_suite(
        self,
        plan_id: int,
        parent_suite_id: int,
        feature_name: str,
        version: str,
        version_type: str = None
    ) -> int:
        logger.info(f"🏗️ Creating feature suite for: '{feature_name}' (Plan: {plan_id}, Parent: {parent_suite_id})")
        logger.info(f"🔄 Version: {version}, Type: {version_type}")

        # Clean the feature name first
        clean_feature_name = feature_name.strip()
        
        # For patch versions: suite name should reflect new patch version
        if version_type == 'patch':
            logger.info(f"🔄 Patch version - Creating suite with updated patch version name...")
        
        # Always create suite with current version
        suite_name = f"{clean_feature_name} - v{version}"
        try:
            suite_id = self.azure_service.find_or_create_suite(plan_id, parent_suite_id, suite_name)
            logger.info(f"✅ Successfully created/found suite: {suite_id} for feature '{clean_feature_name}' with version")
            return suite_id
        except Exception as e:
            logger.warning(f"Failed to create suite with version '{suite_name}': {e}")

        # Fallback: Try without version
        try:
            suite_id = self.azure_service.find_or_create_suite(plan_id, parent_suite_id, clean_feature_name)
            logger.info(f"✅ Successfully created/found suite: {suite_id} for feature '{clean_feature_name}' without version")
            return suite_id
        except Exception as e:
            logger.warning(f"Failed to create suite without version '{clean_feature_name}': {e}")

        # Last resort: Try with a simple unique suffix
        try:
            unique_name = f"{clean_feature_name} - Suite"
            suite_id = self.azure_service.find_or_create_suite(plan_id, parent_suite_id, unique_name)
            logger.info(f"✅ Successfully created/found suite: {suite_id} for feature '{clean_feature_name}' with simple suffix")
            return suite_id
        except Exception as e:
            logger.error(f"❌ Failed to create any suite for feature '{clean_feature_name}': {e}")
            # Never fall back to parent suite - always raise the exception
            raise Exception(f"Could not create suite for feature '{clean_feature_name}': {e}")
