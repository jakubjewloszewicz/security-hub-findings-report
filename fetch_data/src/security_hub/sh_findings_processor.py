from collections import defaultdict
import pandas as pd
from typing import Dict, List, Optional

from src.utils.aws.security_hub import normalize_standard_id
import src.utils.yaml_utils as yaml_utils
from src.security_hub.sh_findings import get_findings_dataframe, sanitize_filename
from src.security_hub.sh_controls import get_standard_controls_dataframe
from src.models import SeverityCounts, ControlStats, FailedControl



def group_findings_by_product():
    all_findings = yaml_utils.read_file_yaml("sh_findings/all.yaml")
    
    # Remove specified fields from each finding
    fields_to_remove = [
        "AwsAccountId",
        'CompanyName',
        # 'CreatedAt',
        # 'Description',
        "FindingProviderFields",
        "FirstObservedAt",
        "Id",
        "LastObservedAt",
        "ProcessedAt",
        'ProductFields',
        "RecordState",
        "Region",
        # 'Remediation',
        # 'Resources', 
        'SchemaVersion', 
        'Types',
        # 'UpdatedAt', 
        'WorkflowState', 
        'Workflow',
    ]
    # Process findings and split by ProductName    # Group findings by ProductName
    findings_by_product = defaultdict(list)

    for finding in all_findings:
        product_name = finding.get("ProductName", "unknown")
        cleaned = {k: v for k, v in finding.items() if k not in fields_to_remove}
        findings_by_product[product_name].append(cleaned)

    # Save each product's findings to a separate file
    print(f"\nFound {len(findings_by_product)} distinct products")
    
    for product_name, findings in findings_by_product.items():
        filename = f"sh_findings/by_product/{sanitize_filename(product_name)}.yaml"
        yaml_utils.save_data_yaml(findings, filename)
        print(f"  - {product_name}: {len(findings)} findings → {filename}")
        
    summary = {
        'total_products': len(findings_by_product),
        'products': [
            {
                'name': product_name,
                'finding_count': len(findings),
                'filename': f"findings_{sanitize_filename(product_name)}.yaml"
            }
            for product_name, findings in sorted(findings_by_product.items())
        ]
    }
    print(summary)
    
def calculate_control_stats(control_status_df: pd.DataFrame) -> ControlStats:
    """Calculate control statistics from aggregated control status."""
    statuses = control_status_df['ComplianceStatus']
    
    return ControlStats(
        passed=int((statuses == 'PASSED').sum()),
        failed=int((statuses == 'FAILED').sum()),
        no_data=int((statuses == 'NOT_AVAILABLE').sum()),
        unknown=int((~statuses.isin(['PASSED', 'FAILED', 'NOT_AVAILABLE'])).sum()),
        disabled=0,
        total=len(control_status_df)
    )

def count_by_severity(df: pd.DataFrame, severity_col: str = 'SeverityLabel') -> SeverityCounts:
    """Count records by severity level."""
    if df.empty:
        return SeverityCounts()
    
    counts = df[severity_col].value_counts().to_dict()
    return SeverityCounts(
        critical=counts.get('CRITICAL', 0),
        high=counts.get('HIGH', 0),
        medium=counts.get('MEDIUM', 0),
        low=counts.get('LOW', 0),
        info=counts.get('INFORMATIONAL', 0)
    )

def generate_doc_url(control_id: str) -> str:
    """Generate AWS documentation URL for a control ID."""
    parts = control_id.split('.')
    service = parts[0].lower()
    control_num = parts[1]
    return f"https://docs.aws.amazon.com/securityhub/latest/userguide/{service}-controls.html#{service}-{control_num}"

def merge_controls_with_findings(all_controls_df: pd.DataFrame, findings_df: pd.DataFrame) -> pd.DataFrame:
    """Merge all controls with aggregated findings, marking controls without findings as NOT_AVAILABLE."""
    control_status_df = all_controls_df.merge(
        findings_df,
        on='GeneratorId',
        how='left'
    )
    
    # Fill missing values for controls without findings
    control_status_df['ComplianceStatus'] = control_status_df['ComplianceStatus'].fillna('NOT_AVAILABLE')
    control_status_df['SeverityLabel'] = control_status_df['SeverityLabel'].fillna(
        control_status_df['SeverityRating']
    )
    
    return control_status_df


def get_critical_high_failed_controls(control_status_df: pd.DataFrame, findings_df: pd.DataFrame) -> List[FailedControl]:
    """Extract failed controls with CRITICAL and HIGH severity, enriched with metadata."""
    # Filter for failed critical/high controls
    failed_critical_high = control_status_df[
        (control_status_df['ComplianceStatus'] == 'FAILED') &
        (control_status_df['SeverityLabel'].isin(['CRITICAL', 'HIGH']))
    ].copy()
    
    if failed_critical_high.empty:
        return []
    
    # Extract control IDs from GeneratorId
    failed_critical_high['ControlId'] = failed_critical_high['GeneratorId'].str.replace(
        'security-control/', '', regex=False
    )
    
    # Get control titles from findings (findings_df already has Title)
    if 'Title' in findings_df.columns:
        control_titles = findings_df.set_index('GeneratorId')['Title']
        failed_critical_high['Title'] = failed_critical_high['GeneratorId'].map(control_titles)
    else:
        failed_critical_high['Title'] = failed_critical_high['ControlId']
    
    # Generate documentation URLs
    failed_critical_high['DocUrl'] = failed_critical_high['ControlId'].apply(generate_doc_url)
    
    # Sort by severity (CRITICAL first) then by control ID
    severity_order = {'CRITICAL': 0, 'HIGH': 1}
    failed_critical_high['_sort'] = failed_critical_high['SeverityLabel'].map(severity_order)
    failed_critical_high = failed_critical_high.sort_values(['_sort', 'ControlId'])
    
    # Convert to FailedControl objects
    return [
        FailedControl(
            control_id=row['ControlId'],
            severity=row['SeverityLabel'],
            title=row['Title'],
            doc_url=row['DocUrl']
        )
        for _, row in failed_critical_high.iterrows()
    ]


def process_standard_findings(standard_id:str) -> Optional[Dict]:
    """
    Process Security Hub findings for a specific standard.
    
    Args:
        controls: Dictionary of all controls mapped by subscription ARN
        findings: List of all Security Hub findings
        standards: List of all Security Hub standards
        standard: The specific standard to process
        
    Returns:
        Dictionary containing standard summary, control statistics, and severity breakdowns
    """
    
    # Log processing information
    print(f'Processing Standard ID: {standard_id}')
    
    # Get control mapping and findings for this standard
    all_controls_df = get_standard_controls_dataframe(standard_id)
    print(f'  Total controls in standard: {len(all_controls_df)}')
    
    findings_df = get_findings_dataframe(standard_id)
    print(f'  Total findings for standard: {len(findings_df)}')
    
    # Build comprehensive control status by merging controls and findings
    control_status_df = merge_controls_with_findings(all_controls_df, findings_df)
        
    print(f'  Controls breakdown: {control_status_df["ComplianceStatus"].value_counts().to_dict()}')
    
    # Calculate statistics
    control_stats = calculate_control_stats(control_status_df)
    
    # Calculate severity breakdowns
    total_severity = count_by_severity(all_controls_df, 'SeverityRating')
    
    failed_controls_df = control_status_df[control_status_df['ComplianceStatus'] == 'FAILED']
    failed_severity = count_by_severity(failed_controls_df, 'SeverityLabel')
    
    # Count failed findings by severity (actual findings, not controls)
    if not findings_df.empty:
        failed_findings_df = findings_df[findings_df['ComplianceStatus'] == 'FAILED']
        finding_counts = count_by_severity(failed_findings_df, 'SeverityLabel')
    else:
        finding_counts = SeverityCounts()
    
    # Get critical and high failed controls with details
    if not findings_df.empty:
        failed_controls = get_critical_high_failed_controls(control_status_df, findings_df)
        failed_controls = [fc.to_dict() for fc in failed_controls]
    else:
        failed_controls = []
    
    # Build report payload
    data= {
        'standard': {
            'id': standard_id,
        },
        'summary': {
            'total_controls': control_stats.total,
            'passed': control_stats.passed,
            'failed': control_stats.failed,
            'no_data': control_stats.no_data,
            'unknown': control_stats.unknown,
            'disabled': control_stats.disabled
        },
        'severity_breakdown': {
            'all_controls': {
                'critical': total_severity.critical,
                'high': total_severity.high,
                'medium': total_severity.medium,
                'low': total_severity.low,
                'informational': total_severity.info
            },
            'failed_controls': {
                'critical': failed_severity.critical,
                'high': failed_severity.high,
                'medium': failed_severity.medium,
                'low': failed_severity.low,
                'informational': failed_severity.info
            },
            'failed_findings': {
                'critical': finding_counts.critical,
                'high': finding_counts.high,
                'medium': finding_counts.medium,
                'low': finding_counts.low,
                'informational': finding_counts.info
            }
        },
        'failed_controls': {
            'critical_and_high': failed_controls,
            'total_count': len(failed_controls)
        }
    }
    yaml_utils.save_data_yaml(data, f'sh_standards/{standard_id}/summary.yaml')
    
def map_standard_findings_to_controls():
    """Map findings to controls for each enabled standard."""
    enabled_standards = yaml_utils.read_file_yaml("sh_standards/enabled.yaml")
    
    for standard in enabled_standards:
        standard_id = normalize_standard_id(standard['StandardsArn'])
        print(f"\nMapping findings to controls for standard: {standard['Name']} ({standard_id})")
        process_standard_findings(standard_id)