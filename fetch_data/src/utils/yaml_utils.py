#!/usr/bin/env python3

from functools import cache
from pathlib import Path
import yaml
import os
import src.env as env

@cache
def read_file_yaml(filename: str):
    file_path = Path("../data") / os.environ.get('CUSTOMER') / os.environ.get('AWS_ACCOUNT_ID') / os.environ.get('REPORTING_DATE') / filename
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
    return data

def save_data_yaml(data, filename):
    data_dir = Path("../data") / os.environ.get('CUSTOMER') / os.environ.get('AWS_ACCOUNT_ID') / os.environ.get('REPORTING_DATE')
    path = data_dir / filename
    os.makedirs(path.parent, exist_ok=True)
    
    with open(path, "w") as f:
        yaml.dump(data, f, indent=4)
    print(f"📄 YAML data written to: {path}")
