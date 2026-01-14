#!/usr/bin/env python3

from pathlib import Path
import os

from src.utils.arg_parser import parse_args
from src import env
from src.to_markdown.generate_report import generate_comprehensive_report_per_account
from src.to_pdf.main import generate_pdf_from_markdown

if __name__ == "__main__":
    
    args = parse_args()
    env.load_environment_variables(args.env_file)
    
    region_name = os.getenv('AWS_REGION')
    account_id = os.getenv('AWS_ACCOUNT_ID')

    outputs_dir = Path("outputs") / os.environ.get('CUSTOMER') / os.environ.get('AWS_ACCOUNT_ID') / os.environ.get('REPORTING_DATE')
    output_file = outputs_dir / "report.md"
    os.makedirs(output_file.parent, exist_ok=True)
    
    markdown_content = generate_comprehensive_report_per_account(account_id, region_name)
    with open(output_file, 'w') as f:
        f.write(''.join(markdown_content))
        
    pdf_path = generate_pdf_from_markdown(output_file, account_id)
    print(f"📄 PDF report generated: {pdf_path}")
