import re
from typing import Dict, List, Any
from app.core.logging import get_logger

logger = get_logger(__name__)


def parse_gherkin(text: str) -> Dict[str, Any]:
    """Parses Gherkin text into a structured dictionary."""
    lines = [l.strip() for l in text.splitlines()]
    # Initialize feature with separate lists for background description and steps
    feature = {"background_description": [], "background_steps": [], "scenarios": [], "feature_name": ""}
    curr, mode = None, "initial"  # Start in an "initial" mode for lines before any block
    ex_h, ex_r = [], []  # These will hold the header and rows for the *current* Examples table

    # Define Gherkin keywords for step identification (case-insensitive check)
    # "قانون:" is NOT in this list as it goes to description. "پیش‌زمینه:" is handled separately for removal.
    gherkin_step_keywords = ("given", "when", "then", "and", "but", "هنگامی که", "و", "آنگاه", "با فرض",
                             "با توجه به اینکه")  # Added "با فرض", "با توجه به اینکه"

    def is_gherkin_step_line(line):
        """Checks if a line starts with a Gherkin step keyword."""
        for keyword in gherkin_step_keywords:
            # Check for keyword followed by space or colon (for "Scenario Outline:")
            if line.lower().startswith(keyword.lower() + " ") or line.lower().startswith(keyword.lower() + ":"):
                return True
        return False

    def finalize_current_scenario():
        """Helper to finalize the current scenario object and add it to feature."""
        nonlocal curr, ex_h, ex_r
        if curr:
            # If the current scenario was an outline and examples were collected
            if curr.get("outline") and ex_h and ex_r:
                # Ensure headers and rows match in length before zipping
                if ex_r and len(ex_h) == len(ex_r[0]):
                    curr["examples"] = [dict(zip(ex_h, row)) for row in ex_r]
                else:
                    logger.warning(
                        f"Example table for scenario '{curr['title']}' has inconsistent column count or is empty. Header count: {len(ex_h)}, First row column count: {len(ex_r[0]) if ex_r else 0}. Examples might be parsed incorrectly or skipped.")
                    curr["examples"] = []
            feature["scenarios"].append(curr)
            debug_examples_count = len(curr.get('examples', []))
            logger.debug(
                f"Appending scenario '{curr['title']}'. Outline: {curr.get('outline')}, Steps count: {len(curr['steps'])}, Examples count: {debug_examples_count}")
            if debug_examples_count > 0:
                logger.debug(f"First example: {curr['examples'][0]}")
        curr = None
        ex_h, ex_r = [], []  # Reset for the next scenario

    for l in lines:
        if not l: continue  # Skip empty lines

        if l.startswith("Feature:") or l.startswith("ویژگی:"):  # Added Persian keyword
            finalize_current_scenario()  # Finalize any previous scenario
            mode = "feature_description_gathering"  # New mode to gather feature description
            # Extract feature name using a regex that matches both "Feature:" and "ویژگی:"
            feature_name_match = re.match(r"(?:Feature|ویژگی):\s*(.*)", l)
            if feature_name_match:
                feature["feature_name"] = feature_name_match.group(1).strip()
            # Do NOT add 'Feature:' line itself to any output list as per user request
            continue

        if l.startswith("Background:") or l.startswith("پیش‌زمینه:"):
            finalize_current_scenario()  # Finalize previous scenario if any
            mode = "background_block"
            # Extract content after "Background:" or "پیش‌زمینه:" and add it as a step
            content_after_keyword = re.sub(r"^(Background:|پیش‌زمینه:)\s*", "", l, flags=re.IGNORECASE).strip()
            if content_after_keyword:  # Only add if there's actual content
                feature["background_steps"].append(l)  # Append the original line, format_steps_xml will clean it
            continue

        if l.startswith("Scenario:") or l.startswith("سناریو:"):
            finalize_current_scenario()  # Finalize previous scenario
            curr = {"title": l.split(":", 1)[1].strip(), "steps": [], "outline": False, "description_parts": []}
            mode = "scenario_block"
            continue

        if l.startswith("Scenario Outline:") or l.startswith("طرح سناریو:"):
            finalize_current_scenario()  # Finalize previous scenario
            curr = {"title": l.split(":", 1)[1].strip(), "steps": [], "outline": True, "description_parts": []}
            mode = "scenario_outline_block"  # New mode for clarity
            continue

        # Handle lines based on current mode
        if mode == "initial" or mode == "feature_description_gathering":
            # Only "قانون:" lines from initial/feature description go to background_description
            if l.startswith("قانون:"):
                feature["background_description"].append(l)
            # All other lines in this mode (like general feature description "درخواست غیر فعال‌سازی...") are discarded from description
            # They are also not steps, so they are effectively ignored for output.
        elif mode == "background_block":
            # If it's a Gherkin step keyword, add to background steps
            if is_gherkin_step_line(l):
                feature["background_steps"].append(l)
            elif l.startswith("قانون:"):  # "قانون:" goes to background description now
                feature["background_description"].append(l)
            # Other lines in background block (e.g., "با فرض کاربر...") are now treated as steps.
            else:
                feature["background_steps"].append(l)
        elif mode in ["scenario_block", "scenario_outline_block"]:
            if l.startswith("Examples:") or l.startswith("مثال‌ها:"):
                mode = "examples_block"
                curr["description_parts"].append(l)  # Add "Examples:" header to description
            elif l.startswith("قانون:"):  # "قانون:" goes to scenario description now
                curr["description_parts"].append(l)
            elif is_gherkin_step_line(l):  # Add to steps if it's a recognized Gherkin step
                curr["steps"].append(l)
            # Other lines in scenario block (not steps, not examples, not rules) are discarded from description
        elif mode == "examples_block":
            if l.startswith("|"):
                cells = [c.strip() for c in l.split('|')[1:-1]]  # Keep empty cells
                if not ex_h:  # First row of table is header
                    ex_h = cells
                else:  # Subsequent rows are data
                    ex_r.append(cells)
                curr["description_parts"].append(l)  # Add example table rows to description
            # Other lines in examples block are discarded from description

    finalize_current_scenario()  # Finalize the last scenario in the file
    return feature


def gherkin_table_to_html(table_lines):
    """Converts a list of Gherkin table lines (starting with '|') into an HTML table."""
    if not table_lines:
        return ""
    html = "<table style='width:100%; border-collapse: collapse; border: 1px solid #ddd;'>"
    for i, line in enumerate(table_lines):
        if line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            tag = "th" if i == 0 else "td"  # First row is header (<th>), others are data (<td>)
            html += "<tr>"
            for cell in cells:
                html += f"<{tag} style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{cell}</{tag}>"
            html += "</tr>"
    html += "</table>"
    return html


def format_description_html(description_parts):
    """Formats a list of description parts into HTML, handling paragraphs, Gherkin tables, and specific rules."""
    html_content = []
    current_paragraph_lines = []
    temp_table_lines = []

    for part in description_parts:
        if part.startswith("Examples:") or part.startswith("مثال‌ها:"):
            # If we were collecting a paragraph, finalize it
            if current_paragraph_lines:
                html_content.append(f"<p>{' '.join(current_paragraph_lines)}</p>")
                current_paragraph_lines = []
            # If there was a previous table, convert it
            if temp_table_lines:
                html_content.append(gherkin_table_to_html(temp_table_lines))
                temp_table_lines = []

            html_content.append(f"<p><strong>{part}</strong></p>")  # Add Examples header as strong text
        elif part.startswith("|"):
            # If we were collecting a paragraph, finalize it
            if current_paragraph_lines:
                html_content.append(f"<p>{' '.join(current_paragraph_lines)}</p>")
                current_paragraph_lines = []
            temp_table_lines.append(part)
        elif part.startswith("قانون:"):  # New: Format "قانون:" specifically for description
            if current_paragraph_lines:
                html_content.append(f"<p>{' '.join(current_paragraph_lines)}</p>")
                current_paragraph_lines = []
            if temp_table_lines:
                html_content.append(gherkin_table_to_html(temp_table_lines))
                temp_table_lines = []
            # Format "قانون:" with strong tag and a distinct style
            html_content.append(f"<p style='font-style: italic; color: #555;'><strong>{part}</strong></p>")
        else:
            # If there was a previous table, convert it
            if temp_table_lines:
                html_content.append(gherkin_table_to_html(temp_table_lines))
                temp_table_lines = []
            current_paragraph_lines.append(part)

    # Finalize any remaining paragraph or table
    if current_paragraph_lines:
        html_content.append(f"<p>{' '.join(current_paragraph_lines)}</p>")
    if temp_table_lines:
        html_content.append(gherkin_table_to_html(temp_table_lines))

    return "\n".join(html_content)


def expand_outlines(scenarios, background_description, background_steps):
    """Turns scenario outlines into single scenarios with parameters, and regular scenarios."""
    out = []
    for s in scenarios:
        logger.debug(
            f"Processing scenario '{s['title']}'. Outline: {s.get('outline')}, Examples present: {s.get('examples') is not None and len(s.get('examples', [])) > 0}")

        # Combine background description with scenario-specific description parts for the full description
        # Description should contain Feature's general description and Examples table
        full_description_parts = list(background_description)  # Start with global background description
        full_description_parts.extend(s["description_parts"])  # Add scenario-specific description parts

        # Debugging prints for description content
        logger.debug(f"background_description content: {background_description}")
        logger.debug(f"s['description_parts'] content: {s['description_parts']}")
        logger.debug(f"Combined full_description_parts: {full_description_parts}")

        base_description_html = format_description_html(full_description_parts)  # Format as HTML
        logger.debug(f"base_description_html (before expansion): '{base_description_html}'")

        # Combine background steps with scenario-specific steps
        combined_steps = list(background_steps)  # Use the passed background_steps
        combined_steps.extend(s["steps"])  # Add scenario's own steps

        if s.get("outline") and s.get("examples"):
            # For Scenario Outline, create ONE test case with parameters

            # 1. Transform steps to use ADO parameter syntax {{param_name}}
            parameterized_steps = []
            for st in combined_steps:  # Use combined_steps here
                line = st
                for k in s["examples"][0].keys():  # Use keys from first example for parameter names
                    placeholder_gherkin = f"<{k}>"
                    placeholder_ado = f"{{{{{k}}}}}"  # Azure DevOps parameter syntax
                    line = line.replace(placeholder_gherkin, placeholder_ado)
                parameterized_steps.append(line)

            # 2. Extract header and data for local parameters XML
            parameters_header = list(s["examples"][0].keys())  # Assuming all examples have same keys
            parameters_data = [list(ex.values()) for ex in s["examples"]]

            # 3. Append this single parameterized scenario
            out.append({
                "title": s["title"],  # Original Scenario Outline title
                "steps": parameterized_steps,
                "description": base_description_html,  # Description is now HTML
                "parameters_header": parameters_header,
                "parameters_data": parameters_data
            })
            logger.debug(
                f"Transformed Scenario Outline '{s['title']}' into a single parameterized scenario.")
        else:
            # For non-outline scenarios, keep as is (no parameters)
            steps = []
            for st in combined_steps:  # Use combined_steps here
                line = st
                # For non-outline scenarios, if there are placeholders, replace them with values from examples.
                # If the value is empty, it will be replaced with an empty string.
                # This assumes that if a non-outline scenario has placeholders, it's because
                # it's intended to be a regular scenario with hardcoded values or a simple substitution.
                # Reverting to previous logic: if value is empty, keep placeholder.
                if s.get("examples"):  # Check if there are examples, even if not an outline
                    for k, v in s["examples"][0].items():  # Use first example's keys/values for replacement
                        placeholder = f"<{k}>"
                        if v:  # Only replace if value is not empty
                            line = line.replace(placeholder, v)
                steps.append(line)

            out.append(
                {"title": s["title"], "steps": steps, "description": base_description_html})  # Description is now HTML
            logger.debug(
                f"Not expanding scenario '{s['title']}'. Outline: {s.get('outline')}, Examples present: {s.get('examples') is not None and len(s.get('examples', [])) > 0}")
    return out 