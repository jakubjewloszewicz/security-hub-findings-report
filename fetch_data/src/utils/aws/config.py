import boto3
import src.utils.yaml_utils as yaml_utils

def fetch_config_conformance_packs(account_id, profile, region):
    """Fetch and save AWS Config conformance packs."""
    print("            🔬 Config - Conformance Packs\n")
    session = boto3.Session(profile_name=profile, region_name=region)
    c = session.client('config')
    
    print("\n📋 Fetching AWS Config Conformance Packs...\n")
    
    response = c.describe_conformance_packs()
    conformance_packs = response.get('ConformancePackDetails', [])
    
    yaml_utils.save_data_yaml(conformance_packs, "config/conformance_packs.yaml")
    return conformance_packs
