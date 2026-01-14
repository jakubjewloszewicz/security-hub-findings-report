import src.utils.aws.config as config_utils

def fetch_config_conformance_packs(account_id, profile, region):
    """Fetch and save AWS Config conformance packs."""
    
    conformance_packs = config_utils.fetch_config_conformance_packs(account_id, profile, region)
    if not conformance_packs:
        print("⚠️  No conformance packs are currently enabled.")
    
    print("\n" + "="*80)
