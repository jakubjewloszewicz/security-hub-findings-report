from glob import glob
import os
import sys
import glob
from dotenv import load_dotenv
from src.utils.arg_parser import parse_args
import src.utils.aws.sts as sts

# List of regions to query for each profile
regions = [
    'us-east-1', 
    'eu-west-1', 
    'eu-north-1'
]

"""
Environment variable loading utilities for Athena query scripts
"""

def load_environment_variables(env_file_path='.env'):
    """
    Load environment variables from specified .env file with validation
    
    Args:
        env_file_path (str): Path to the environment file
        
    Raises:
        SystemExit: If the environment file is not found
    """
    if not os.path.exists(env_file_path):
        print(f"❌ Environment file '{env_file_path}' not found!")
        sys.exit(1)
        
    env_files = glob.glob('.env.*')
    if not env_files:
        print("❌ No .env files found. Please create .env files for your accounts.")
        print("   Example: .env.test, .env.prod")
        sys.exit(1)
    print(f"📄 Loading environment variables from: {env_file_path}")
    load_dotenv()
    load_dotenv(env_file_path, override=True)
    
    account_id = os.getenv('AWS_ACCOUNT_ID')
    aws_profile = os.getenv('AWS_PROFILE')
    
    if not account_id:
        print(f"⚠️  Failing : AWS_ACCOUNT_ID not found")
        sys.exit(1)
    if not aws_profile:
        print(f"⚠️  Failing : AWS_PROFILE not found")
        sys.exit(1)
        
def setup_aws_environment():
    """Parse arguments, load environment variables, and validate AWS configuration."""
    args = parse_args()
    load_environment_variables(args.env_file)
    
    profile = os.getenv('AWS_PROFILE')
    region = os.getenv('AWS_REGION')
    account_id = os.getenv('AWS_ACCOUNT_ID')
    
    print(f"🔑 Using AWS profile: {profile}")
    print(f"📍 Account: {account_id}, Region: {region}\n")
    sts.validate_aws_account(account_id)
    
    return profile, region, account_id