import src.utils.aws.control_tower as control_tower

def fetch_control_tower_controls(account_id):
    """Fetch Control Tower control catalog and enabled controls."""
    print("\n🔬 Control Tower - Controls\n")
    catalog = control_tower.fetch_control_tower_control_catalog()
    print(f"\n✅ Fetched {len(catalog)} Control Tower catalog entries available for account {account_id}.\n")
    controls = control_tower.fetch_enabled_control_tower_controls()
    print(f"\n✅ Fetched {len(controls)} Control Tower controls enabled for account {account_id}.\n")
