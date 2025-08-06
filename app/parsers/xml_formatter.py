import re
from xml.etree.ElementTree import Element, SubElement, tostring
from typing import List, Dict, Any
from app.core.logging import get_logger

logger = get_logger(__name__)


def format_steps_xml(steps: List[str]) -> str:
    """Formats a list of Gherkin steps into Azure DevOps Test Case XML."""
    root = Element('steps', {'id': '0', 'last': str(len(steps))})
    
    for idx, st in enumerate(steps, start=1):
        # Remove only "Background:" or "پیش‌زمینه:" from the start of the step text.
        # Other Gherkin keywords are preserved.
        clean = st
        # Regex to remove "Background:" or "پیش‌زمینه:" from the start, case-insensitive.
        # This regex will only match if "Background:" or "پیش‌زمینه:" is at the very beginning of the string.
        clean = re.sub(r"^(Background:|پیش‌زمینه:)\s*", "", st, flags=re.IGNORECASE).strip()

        step_elem = SubElement(root, 'step', {'id': str(idx), 'type': 'ActionStep'})
        # 'parameterizedString' for the action
        ps_action = SubElement(step_elem, 'parameterizedString', {'isformatted': 'true'})
        ps_action.text = str(clean)
        # Add an empty 'parameterizedString' for the expected result, as per common ADO format
        ps_expected = SubElement(step_elem, 'parameterizedString', {'isformatted': 'true'})
        ps_expected.text = ""
    
    xml_str = tostring(root, encoding='utf-8').decode('utf-8')
    return '<?xml version="1.0" encoding="utf-8"?>' + xml_str


def format_local_parameters_xml(header: List[str], data: List[List[str]]) -> str:
    """Formats header and data for local parameters into Azure DevOps XML."""
    root = Element('parameters')
    
    # Add parameter definitions
    for idx, h_item in enumerate(header, start=1):
        # Note 'parametr' not 'parameter' as per common ADO XML quirk
        param_elem = SubElement(root, 'parametr', {'id': str(idx), 'name': h_item})

    # Add data rows
    data_elem = SubElement(root, 'data')
    for row_idx, row_data in enumerate(data):
        row_elem = SubElement(data_elem, 'row')
        for col_idx, item_value in enumerate(row_data):
            # Note 'param' attribute points to the parameter's ID
            item_elem = SubElement(row_elem, 'item', {'param': str(col_idx + 1)})
            item_elem.text = item_value  # Value for the item

    xml_str = tostring(root, encoding='utf-8').decode('utf-8')
    return xml_str 