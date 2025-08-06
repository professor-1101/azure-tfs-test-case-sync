from typing import Dict, List, Any
from app.core.logging import get_logger

logger = get_logger(__name__)


def parse_json_content(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """Parses JSON content into the same structure as Gherkin parser."""
    
    # Initialize the feature structure
    feature = {
        "background_description": [],
        "background_steps": [],
        "scenarios": [],
        "feature_name": json_data.get("name", "")
    }
    
    # Process each feature in the JSON
    for feature_data in json_data.get("features", []):
        feature_name = feature_data.get("name", "")
        feature_description = feature_data.get("description", "")
        
        # Add feature description to background_description
        if feature_description:
            feature["background_description"].append(f"قانون: {feature_description}")
        
        # Process background steps if present
        background = feature_data.get("background", {})
        if background and "steps" in background:
            for step in background["steps"]:
                keyword = step.get("keyword", "")
                text = step.get("text", "")
                if keyword and text:
                    feature["background_steps"].append(f"{keyword} {text}")
        
        # Process scenarios
        for scenario in feature_data.get("scenarios", []):
            scenario_title = scenario.get("name", "")
            scenario_description = scenario.get("description", "")
            scenario_type = scenario.get("type", "scenario")
            
            # Create scenario object
            scenario_obj = {
                "title": scenario_title,
                "steps": [],
                "outline": scenario_type == "scenario-outline",
                "description_parts": []
            }
            
            # Add scenario description
            if scenario_description:
                scenario_obj["description_parts"].append(scenario_description)
            
            # Process scenario steps
            for step in scenario.get("steps", []):
                keyword = step.get("keyword", "")
                text = step.get("text", "")
                if keyword and text:
                    scenario_obj["steps"].append(f"{keyword} {text}")
            
            # Process examples for scenario outlines
            examples = scenario.get("examples", {})
            if examples and scenario_type == "scenario-outline":
                headers = examples.get("headers", [])
                rows = examples.get("rows", [])
                
                if headers and rows:
                    # Convert to the format expected by expand_outlines
                    examples_list = []
                    for row in rows:
                        row_values = row.get("values", [])
                        if len(row_values) == len(headers):
                            example_dict = dict(zip(headers, row_values))
                            examples_list.append(example_dict)
                    
                    scenario_obj["examples"] = examples_list
                    
                    # Add examples table to description
                    scenario_obj["description_parts"].append("Examples:")
                    header_line = "| " + " | ".join(headers) + " |"
                    scenario_obj["description_parts"].append(header_line)
                    
                    for row in rows:
                        row_values = row.get("values", [])
                        row_line = "| " + " | ".join(row_values) + " |"
                        scenario_obj["description_parts"].append(row_line)
            
            feature["scenarios"].append(scenario_obj)
    
    logger.info(f"Parsed JSON content: {len(feature['scenarios'])} scenarios found")
    return feature


def convert_json_to_gherkin_format(json_data: Dict[str, Any]) -> str:
    """Converts JSON content to Gherkin text format for compatibility."""
    
    gherkin_lines = []
    
    # Add feature header
    feature_name = json_data.get("name", "Feature")
    gherkin_lines.append(f"Feature: {feature_name}")
    
    # Process each feature
    for feature_data in json_data.get("features", []):
        feature_name = feature_data.get("name", "")
        feature_description = feature_data.get("description", "")
        
        if feature_description:
            gherkin_lines.append(f"قانون: {feature_description}")
        
        # Add background if present
        background = feature_data.get("background", {})
        if background and "steps" in background:
            gherkin_lines.append("Background:")
            for step in background["steps"]:
                keyword = step.get("keyword", "")
                text = step.get("text", "")
                if keyword and text:
                    gherkin_lines.append(f"  {keyword} {text}")
        
        # Process scenarios
        for scenario in feature_data.get("scenarios", []):
            scenario_title = scenario.get("name", "")
            scenario_description = scenario.get("description", "")
            scenario_type = scenario.get("type", "scenario")
            
            # Add scenario header
            if scenario_type == "scenario-outline":
                gherkin_lines.append(f"Scenario Outline: {scenario_title}")
            else:
                gherkin_lines.append(f"Scenario: {scenario_title}")
            
            # Add scenario description
            if scenario_description:
                gherkin_lines.append(f"  {scenario_description}")
            
            # Add scenario steps
            for step in scenario.get("steps", []):
                keyword = step.get("keyword", "")
                text = step.get("text", "")
                if keyword and text:
                    gherkin_lines.append(f"    {keyword} {text}")
            
            # Add examples for scenario outlines
            if scenario_type == "scenario-outline":
                examples = scenario.get("examples", {})
                headers = examples.get("headers", [])
                rows = examples.get("rows", [])
                
                if headers and rows:
                    gherkin_lines.append("  Examples:")
                    header_line = "    | " + " | ".join(headers) + " |"
                    gherkin_lines.append(header_line)
                    
                    for row in rows:
                        row_values = row.get("values", [])
                        row_line = "    | " + " | ".join(row_values) + " |"
                        gherkin_lines.append(row_line)
            
            gherkin_lines.append("")  # Empty line between scenarios
    
    return "\n".join(gherkin_lines) 