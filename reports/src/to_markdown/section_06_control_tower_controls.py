import re
import yaml
from pathlib import Path
from tabulate import tabulate

from src.to_markdown.markown_printer import MarkdownPrinter
import src.utils.yaml_utils as yaml_utils

class ControlTowerControls(MarkdownPrinter):

    def to_markdown(self, account_id, region_name, *args, **kwargs):

        ct_controls = yaml_utils.read_file_yaml("ct/controls_enabled.yaml")
        ct_controls_reference = yaml_utils.read_file_yaml("ct/control_catalog.yaml")

        markdown_content = []
        markdown_content.append(f"""


<hr class='section-pagebreak'>

## 6. AWS Control Tower: Enabled Controls

This section lists all Control Tower controls that are currently enabled in AWS management account.

""")

        if not ct_controls:
            markdown_content.append(f"""

*No data for Control Tower controls available*.

""")
        else:
            enabled_control_arns = set([control.get('controlIdentifier', '') for control in ct_controls])
            print(len(enabled_control_arns))

            controls = []
            # Add all controls from reference that are enabled
            for control in ct_controls_reference:
                if control.get("Arn") in enabled_control_arns:
                    controls.append([
                        control.get("Name", ""),
                        control.get("Description", ""),
                    ])
            # Add any enabled control ARNs not found in reference
            reference_arns = set([c.get("Arn") for c in ct_controls_reference])
            
            # these cannot be modified
            # https://docs.aws.amazon.com/en_us/controltower/latest/controlreference/cannot-change-with-gr-api.html
            
            legacy_controls = []
            missing_arns = enabled_control_arns - reference_arns
            missing_arns = [s.split('/')[-1] for s in missing_arns]
            for arn in missing_arns:
                legacy_controls.append(f"- `{arn}`")
            controls_markdown = tabulate(controls, headers=["Control Tower control", "Description"], tablefmt="pipe", colalign=["left", "left"])
            markdown_content.append(f"""

{controls_markdown}

**Total enabled Control Tower controls:** {len(controls)} controls enabled.

The following legacy controls are also enabled but their details are not available:

See [legacy controls that cannot be changed with the AWS Control Tower APIs](https://docs.aws.amazon.com/en_us/controltower/latest/controlreference/cannot-change-with-gr-api.html) for more information.

""")
    
            markdown_content.append("""
                            
To enable Control Tower controls, please visit the AWS Control Tower console.

[Open AWS Control Tower Console](https://eu-north-1.console.aws.amazon.com/controltower/home/controls?region=eu-north-1)

""")
        return markdown_content