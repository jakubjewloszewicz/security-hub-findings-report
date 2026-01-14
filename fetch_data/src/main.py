#!/usr/bin/env python3

import src.env as env
from src.security_hub import sh_controls, sh_standards, sh_findings, sh_findings_processor
from src.control_tower import ct_baselines, ct_controls
from src.config import c_conformance_packs

if __name__ == "__main__":
    """Main function to orchestrate all data fetching operations."""
    profile, region, account_id = env.setup_aws_environment()
    
    # sh_findings.fetch_security_hub_findings(profile, region)
    # sh_findings_processor.group_findings_by_product()
    # sh_standards.fetch_security_hub_standards(profile, region)
    # sh_controls.fetch_security_hub_controls(profile, region)
    # sh_findings_processor.map_standard_findings_to_controls()
    # c_conformance_packs.fetch_config_conformance_packs(account_id, profile, region)
    # ct_baselines.fetch_control_tower_baselines(account_id)
    ct_controls.fetch_control_tower_controls(account_id)
