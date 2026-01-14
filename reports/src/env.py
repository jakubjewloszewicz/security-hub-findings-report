from glob import glob
import os
import sys
import glob
from dotenv import load_dotenv
from src.utils.arg_parser import parse_args

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
    load_dotenv(env_file_path, override=True)
    
    account_id = os.getenv('AWS_ACCOUNT_ID')
    aws_profile = os.getenv('AWS_PROFILE')
    customer = os.getenv('CUSTOMER')
    reporting_date = os.getenv('REPORTING_DATE')
    
    if not account_id:
        print(f"⚠️  Failing : AWS_ACCOUNT_ID not found")
        sys.exit(1)
    if not aws_profile:
        print(f"⚠️  Failing : AWS_PROFILE not found")
        sys.exit(1)
    if not customer:
        print(f"⚠️  Failing : CUSTOMER not found")
        sys.exit(1)
    if not reporting_date:
        print(f"⚠️  Failing : REPORTING_DATE not found")
        sys.exit(1)

