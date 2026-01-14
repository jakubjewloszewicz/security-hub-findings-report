
from datetime import datetime
from src.to_markdown.markown_printer import MarkdownPrinter
import src.utils.yaml_utils as yaml_utils
from jinja2 import Environment, FileSystemLoader

jinja_env = Environment(loader=FileSystemLoader('src/to_markdown/templates'))

class TopFindingsAppendix(MarkdownPrinter):
    def to_markdown(self, account_id, region_name, *args, **kwargs):
        
        sh_findings = yaml_utils.read_file_yaml("sh_findings/by_product/security_hub.yaml")
        
        # Filter for FAILED findings only
        failed_findings = [f for f in sh_findings if f.get('Compliance', {}).get('Status') == 'FAILED']
        
        # Group findings by severity
        critical_findings = [f for f in failed_findings if f.get('Severity', {}).get('Label') == 'CRITICAL']
        high_findings = [f for f in failed_findings if f.get('Severity', {}).get('Label') == 'HIGH']

        template = jinja_env.get_template('section_appendix_01_top_findings.md.j2')
        return [template.render(
            critical_findings=critical_findings,
            high_findings=high_findings,
            failed_findings=failed_findings
        )]
        