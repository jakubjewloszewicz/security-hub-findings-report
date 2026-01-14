
import src.utils.aws.control_tower as control_tower
import src.utils.yaml_utils as yaml_utils
import pandas as pd

def fetch_control_tower_baselines(account_id):
    """Fetch, merge, and save Control Tower baselines."""
    print("\n🔬 Control Tower - Baselines\n")
    all_baselines = control_tower.fetch_all_control_tower_baselines()
    enabled_baselines = control_tower.fetch_enabled_control_tower_baselines()

    # Build a set of enabled baseline identifiers for quick lookup
    enabled_ids = {b['baselineIdentifier'] for b in enabled_baselines}

    df_all = pd.DataFrame(all_baselines)
    df_enabled = pd.DataFrame(enabled_baselines)

    # Merge on arn (from all) and baselineIdentifier (from enabled)
    merged = pd.merge(
        df_all,
        df_enabled,
        left_on="arn",
        right_on="baselineIdentifier",
        how="right",
        suffixes=("", "_enabled")
    )
    result = merged.where(pd.notnull(merged), None)  # Replace NaN with None

    # Save to YAML
    yaml_utils.save_data_yaml(result.to_dict(orient="records"), "ct/baselines_merged.yaml")
    print("✅ Investigation complete!")

