#!/usr/bin/env python3

from typing import Dict, List, Optional
from dataclasses import dataclass
import src.utils.yaml_utils as yaml_utils

from src.to_markdown.markown_printer import MarkdownPrinter

@dataclass
class ControlStats:
    """Statistics for control compliance status."""
    passed: int
    failed: int
    no_data: int
    unknown: int
    disabled: int
    total_controls: int
    
    @property
    def security_score(self) -> int:
        """Calculate security score percentage."""
        return int((self.passed / self.total_controls * 100)) if self.total_controls > 0 else 0


@dataclass
class SeverityCounts:
    """Counts by severity level."""
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    informational: int = 0


@dataclass
class FailedControl:
    """Failed control with metadata."""
    control_id: str
    severity: str
    title: str
    doc_url: str


def normalize_standard_id(standard_arn: str) -> str:
    """Normalize standard ID by replacing colons and slashes with underscores."""
    # Example: arn:aws:securityhub:eu-north-1::standards/cis-aws-foundations-benchmark/v/5.0.0
    parts = standard_arn.split('/')
    standard_id = parts[-3] + '_' + parts[-2] + '_' + parts[-1]
    return standard_id

class SecurityHubStandardSummarySection(MarkdownPrinter):
    """Generate Security Hub standard summary markdown report."""
    
    template_name = "section_02_sh_standard_summary.md.j2"
    
    def to_markdown(self, account_id: str, region_name: str, *args, **kwargs) -> List[str]:
        
        enabled_standards = yaml_utils.read_file_yaml("sh_standards/enabled.yaml")
        
        standards_data = []
        
        for standard in enabled_standards:
            standard_id = normalize_standard_id(standard_arn=standard['StandardsArn'])
            standard_summary = yaml_utils.read_file_yaml(f"sh_standards/{standard_id}/summary.yaml")
            
            # Convert to dataclass objects for template
            standard_summary['summary'] = ControlStats(**standard_summary['summary'])
            standard_summary['severity_breakdown']['failed_controls'] = SeverityCounts(**standard_summary['severity_breakdown']['failed_controls'])
            standard_summary['severity_breakdown']['all_controls'] = SeverityCounts(**standard_summary['severity_breakdown']['all_controls'])
            standard_summary['failed_controls']['critical_and_high'] = [
                FailedControl(**control) for control in standard_summary['failed_controls']['critical_and_high']
            ]
            
            standards_data.append(standard_summary)
            
        if not standards_data:
            return ["No enabled standards found."]
        
        return [self.template.render(standards_data=standards_data)]