
import re
from src.to_markdown.markown_printer import MarkdownPrinter
import src.utils.yaml_utils as yaml_utils        

class EnabledConformancePacksSection(MarkdownPrinter):

    template_name = "section_03_config_enabled_conformance_packs.md.j2"

    def to_markdown(self, account_id, region_name, *args, **kwargs):
        
        conformance_packs = yaml_utils.read_file_yaml("config/conformance_packs.yaml")

        arn_pattern = re.compile(r"::standards/(?P<std_code>[^/]+)/v/(?P<std_version>[^/]+)")
        link = lambda std_code, std_version: f"https://{region_name}.console.aws.amazon.com/securityhub/home?region={region_name}#/standards/{std_code}-{std_version}"

        # Prepare conformance packs data
        packs_data = []
        for cp in conformance_packs:
            std_name = cp.get('ConformancePackName', 'N/A')
            match = arn_pattern.search(cp.get('ConformancePackArn', ''))
            if match:
                standard_link = link(match.group('std_code'), match.group('std_version'))
            else:
                standard_link = ""
            packs_data.append({
                'name': std_name,
                'standard_link': standard_link
            })

        rendered_markdown = self.template.render(
            account_id=account_id,
            region_name=region_name,
            conformance_packs=packs_data
        )
        return [rendered_markdown]