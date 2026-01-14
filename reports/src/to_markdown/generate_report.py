from ast import List
from src.to_markdown.markown_printer import MarkdownPrinter
from src.to_markdown import *

# return all sections that should be included in the report
from src.to_markdown.section_00_cover_page import *
from src.to_markdown.section_01_sh_enabled_standards import *
from to_markdown.section_02_sh_standard_summary import *
from src.to_markdown.section_03_config_enabled_conformance_packs import *
from src.to_markdown.section_04_config_findings_summary import *
from src.to_markdown.section_05_control_tower_baselines import ControlTowerBaselines
from to_markdown.section_06_control_tower_controls import ControlTowerControls
from src.to_markdown.section_appendix_01_top_findings import TopFindingsAppendix 

def get_report_sections():
    return [
        CoverPageSection(),
        EnabledSecurityHubStandardsSection(),
        SecurityHubStandardSummarySection(),
        EnabledConformancePacksSection(),
        ConfigFindingsSummarySection(),
        # ConfigConformancePackDetailSection(),
        ControlTowerBaselines(),
        ControlTowerControls(),
        TopFindingsAppendix(),
    ]

def generate_comprehensive_report_per_account(account_id, region_name):

    generators: List[MarkdownPrinter] = get_report_sections()
    
    markdown_content = []
    for generator in generators:
        markdown_content += generator.to_markdown(
            account_id=account_id,
            region_name=region_name,
        )

    return markdown_content
