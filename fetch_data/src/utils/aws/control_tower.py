import os
import boto3
import src.utils.yaml_utils as yaml_utils


def fetch_all_control_tower_baselines():
    """
    Fetch all Control Tower baselines for the given AWS account.
    """
    session = boto3.Session()
    ct = session.client('controltower')
    
    response = ct.list_baselines()

    all_baselines = response.get('baselines', [])

    if not all_baselines:
        print("⚠️  No CT baselines are fetched.")
        return all_baselines
    
    yaml_utils.save_data_yaml(all_baselines, "ct/baselines_all.yaml")
    
    return all_baselines

def fetch_enabled_control_tower_baselines():
    """
    Fetch enabled Control Tower baselines for the given AWS account.
    """
    session = boto3.Session(profile_name=os.getenv("AWS_MGMT_PROFILE"))
    ct = session.client('controltower')

    response = ct.list_enabled_baselines()

    enabled_baselines = response.get('enabledBaselines', [])

    if not enabled_baselines:
        print("⚠️  No CT baselines are fetched.")
        return enabled_baselines

    yaml_utils.save_data_yaml(enabled_baselines, "ct/baselines_enabled.yaml")

    return enabled_baselines


def fetch_control_tower_control_catalog():
    """
    Fetch Control Tower control catalog for the given AWS account.
    """
    session = boto3.Session(profile_name=os.getenv("AWS_MGMT_PROFILE"))
    cc = session.client('controlcatalog')


    catalog = []
    next_token = None
    
    while True:
        print(f"⏳ Fetching control catalog entries... Retrieved so far: {len(catalog)}")
        if next_token:
            response = cc.list_controls(
                MaxResults=100,
                NextToken=next_token
            )
        else:
            response = cc.list_controls(
                MaxResults=100
            )
        print(f"    ➕ Fetched: {len(response.get('Controls', []))} controls")
        
        catalog.extend(response.get('Controls', []))
        next_token = response.get('NextToken')
        
        if not next_token:
            break

    if not catalog:
        print("⚠️  No CT control catalog is fetched.")
        return catalog

    yaml_utils.save_data_yaml(catalog, "ct/control_catalog.yaml")

    return catalog

def fetch_enabled_control_tower_controls():
    """
    Fetch enabled Control Tower controls for the given AWS account.
    """
    session = boto3.Session(profile_name=os.getenv("AWS_MGMT_PROFILE"))
    ct = session.client('controltower')

    response = ct.list_enabled_controls()

    enabled_controls = response.get('enabledControls', [])

    if not enabled_controls:
        print("⚠️  No CT controls are fetched.")
        return enabled_controls
    
    yaml_utils.save_data_yaml(enabled_controls, "ct/controls_enabled.yaml")

    return enabled_controls