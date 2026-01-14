
from src.to_markdown.markown_printer import MarkdownPrinter
import src.utils.yaml_utils as yaml_utils


class EnabledSecurityHubStandardsSection(MarkdownPrinter):
    template_name = "section_01_sh_enabled_standards.md.j2"
    
    def to_markdown(self, account_id, region_name, *args, **kwargs):
        
        sh_standards = yaml_utils.read_file_yaml("sh_standards/all_with_enabled.yaml")
        
        return [self.template.render(
            account_id=account_id,
            region_name=region_name,
            standards=sh_standards
        )]