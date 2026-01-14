
import re
import yaml
from pathlib import Path
from tabulate import tabulate

from src.to_markdown.markown_printer import MarkdownPrinter
import src.utils.yaml_utils as yaml_utils

class ControlTowerBaselines(MarkdownPrinter):

    def to_markdown(self, account_id, region_name, *args, **kwargs):
        
        
        ct_baselines = yaml_utils.read_file_yaml("ct/baselines_merged.yaml")
        
        markdown_content = []
        markdown_content.append(f"""

<hr class='section-pagebreak'>

## 5. AWS Control Tower: Baselines

This section lists all Control Tower baselines.

""")

        if not ct_baselines:
            markdown_content.append(f"""

*No data for Control Tower baselines available*.

""")
        else:
            table = []
            for b in ct_baselines:
                name = b.get('name', 'N/A')
                desc = b.get('description', '')
                status = b.get('status', 'N/A')
                
                # Determine enabled status and emoji
                emoji = "✅" if b.get('arn_enabled', False) else "❌"
                table.append([name, desc, f"{emoji}"])
            markdown_content.append(tabulate(table, headers=["CControl Tower baseline", "Description", "Enabled"], tablefmt="pipe", colalign=["left", "left", "center"]) + "\n")
        
            markdown_content.append(f"\n\n")
            markdown_content.append(f"""

**Total enabled Control Tower baselines:** {len([s for s in ct_baselines if s.get('arn_enabled', False)])}
""")
    
            markdown_content.append("""
                            
To enable Control Tower baselines, please visit the AWS Control Tower console.

[Open AWS Control Tower Console](https://eu-north-1.console.aws.amazon.com/controltower/home/settings?region=eu-north-1)

""")
        return markdown_content