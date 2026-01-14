
import os
import pandas as pd
from src.utils.aws import security_hub
from src.utils.aws.security_hub import normalize_standard_id
import src.utils.yaml_utils as yaml_utils


# Constants for control status and severity priorities
STATUS_PRIORITY = {'FAILED': 0, 'WARNING': 1, 'PASSED': 2, 'NOT_AVAILABLE': 3}
SEVERITY_PRIORITY = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'INFORMATIONAL': 4}


def sanitize_filename(product_name: str) -> str:
    """Convert product name to safe filename."""
    return product_name.replace(" ", "_").replace("/", "_").lower()

def get_worst_status(statuses: pd.Series) -> str:
    """Select the worst compliance status from a series of statuses."""
    return min(statuses, key=lambda x: STATUS_PRIORITY.get(x, 99))

def get_worst_severity(severities: pd.Series) -> str:
    """Select the worst severity level from a series of severities."""
    return min(severities, key=lambda x: SEVERITY_PRIORITY.get(x, 99))

def get_findings_dataframe(standard_id: str) -> pd.DataFrame:
    
    sh_findings = yaml_utils.read_file_yaml("sh_findings/by_product/security_hub.yaml")
    """Filter findings for a specific standard and convert to DataFrame."""
    expanded = []
    for finding in sh_findings:
        associated_standards = finding.get('Compliance', {}).get('AssociatedStandards', [])
        for std in associated_standards:
            if normalize_standard_id(std.get('StandardsId')) == standard_id:
                expanded.append({
                    'GeneratorId': finding.get('GeneratorId'),
                    'Title': finding.get('Title'),
                    'SeverityLabel': finding.get('Severity', {}).get('Label'),
                    'ComplianceStatus': finding.get('Compliance', {}).get('Status'),
                })
    yaml_utils.save_data_yaml(expanded, f'sh_findings/by_standard/{standard_id}/all.yaml')
    findings_df = pd.DataFrame(expanded)
    if findings_df.empty:
        return pd.DataFrame(columns=['GeneratorId', 'Title', 'ComplianceStatus', 'SeverityLabel'])
    
    return findings_df.groupby('GeneratorId').agg({
        'ComplianceStatus': get_worst_status,
        'SeverityLabel': get_worst_severity,
        'Title': 'first'
    }).reset_index()
    
    
def fetch_security_hub_findings(profile, region):
    """Fetch and process Security Hub and AWS Config findings."""
    # findings = yaml_utils.read_file_yaml("sh_findings/all.yaml")
    findings = security_hub.fetch_all_findings(profile, os.environ.get('AWS_ACCOUNT_ID'), region)

    print(f"🔍 Total findings retrieved: {len(findings)}")
    print("\n" + "="*80)
    
    return findings

