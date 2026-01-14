import pandas as pd
import src.utils.yaml_utils as yaml_utils
import src.utils.aws.security_hub as security_hub

def map_to_control_id(remediation_url: str) -> str:
    """Map ControlId to GeneratorId format."""
    # example format   https://docs.aws.amazon.com/console/securityhub/{ControlId}/remediation
    return remediation_url.split('/')[-2]

def get_control_id_map(all_controls: list, standard_id: str) -> dict:
    """Create a mapping from ControlId to control details."""
    
    control_id_map = {}
    for control in all_controls:
        remediation_url = control.get('RemediationUrl', '')
        control_id = map_to_control_id(remediation_url)
        control_id_map[control_id] = control
    return control_id_map


def create_all_controls_dataframe(control_id_map: dict) -> pd.DataFrame:
    """Create a DataFrame with all controls from the standard."""
    return pd.DataFrame([
        {
            'GeneratorId': f'security-control/{ctrl_id}',
            'ControlId': ctrl_id,
            'SeverityRating': control_info.get('SeverityRating', 'UNKNOWN')
        }
        for ctrl_id, control_info in control_id_map.items()
    ])
    
def get_standard_controls_dataframe(standard_id: str) -> dict:
    """Fetch and return controls for a specific standard as a DataFrame."""
    control_id_map = yaml_utils.read_file_yaml(f'sh_standards/{standard_id}/control_map.yaml')
    return create_all_controls_dataframe(control_id_map)
    
def fetch_security_hub_controls(profile, region):
    """Fetch and process Security Hub controls for enabled standards."""
    print("\n🔬 Security Hub - Controls\n")
    all_standards = yaml_utils.read_file_yaml("sh_standards/all.yaml")
    
    print("\n📊 All Security Hub Standards:\n")
    for s in all_standards:
        print(f"{s['Name']}")
    
    print("\n📊 Enabled Security Hub Standards:\n")
    enabled_standards = yaml_utils.read_file_yaml("sh_standards/enabled.yaml")
    
    for enabled_standard in enabled_standards:
        standard_arn = enabled_standard['StandardsArn']
        standard_name = [s for s in all_standards if s['StandardsArn'] == standard_arn][0].get('Name', 'Unknown')
        print(f"Enabled Standard: {standard_name}")
        enabled_standard['Name'] = standard_name

    standard_subscription_arns = [s['StandardsSubscriptionArn'] for s in enabled_standards]
    fetch_all_standard_controls(standard_subscription_arns, profile, region)
    
    print("\n" + "="*80)
    
def fetch_all_standard_controls(subscription_arns, profile, region):
    """
    Describe standards controls for a list of subscription ARNs
    """
    for subscription_arn in subscription_arns:
        standard_id = security_hub.normalize_standard_id(subscription_arn)
        controls = security_hub.fetch_standards_controls(subscription_arn, profile, region)

        control_id_map = get_control_id_map(controls, standard_id)
        yaml_utils.save_data_yaml(control_id_map, f'sh_standards/{standard_id}/control_map.yaml')

