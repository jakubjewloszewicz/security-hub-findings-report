#!/usr/bin/env python3

from pathlib import Path
import os
import yaml
from datetime import datetime
import src.common.env as env
from src.common.arg_parser import parse_sh_args
from src.common.env_loader import load_environment_variables
from src.to_markdown.generate_report import generate_comprehensive_report_per_account

if __name__ == "__main__":
    """
    Generate comprehensive reports for all accounts with compliance data
    
    Returns:
        list: List of paths to generated markdown files
    """
    args = parse_sh_args()
    
    # Load environment
    print(f"📄 Loading environment from: {args.env_file}\n")
    load_environment_variables(args.env_file)  
    
    profile = os.getenv('AWS_PROFILE')
    region_name = os.getenv('AWS_REGION')
    account_id = os.getenv('AWS_ACCOUNT_ID')

    data_dir = Path("data") / env.CUSTOMER / account_id / env.REPORTING_DATE
    markdown_dir = Path("markdown") / env.CUSTOMER / account_id / env.REPORTING_DATE
    markdown_dir.mkdir(exist_ok=True)
    
    print(data_dir)
    findings_file = data_dir / "sh_all_findings.yaml"
    with open(findings_file, 'r') as f:
        all_findings = yaml.safe_load(f)
    
    print(f"\n📊 Processing account: {account_id}")
    markdown_content = generate_comprehensive_report_per_account(account_id, region_name)
    # Write markdown file
    output_file = markdown_dir / "report.md"
    with open(output_file, 'w') as f:
        f.write(''.join(markdown_content))
    
    print(f"✅ Comprehensive report generated: {output_file}")
    print(f"\n{'='*80}")
