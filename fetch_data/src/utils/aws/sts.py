
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def validate_aws_account(expected_account_id):
    """
    Validate that the current AWS account matches the expected account ID
    
    Args:
        expected_account_id: Expected AWS account ID
    """
    # Clear default boto3 session to force new credentials
    boto3.DEFAULT_SESSION = None
    try:
        sts_client = boto3.client('sts')
        actual_account_id = sts_client.get_caller_identity()['Account']
    except (NoCredentialsError, PartialCredentialsError):
        print("❌ AWS CLI is not configured or credentials are invalid.")
        print("Please run 'aws configure' or check your AWS credentials.")
        exit(1)

    if actual_account_id != expected_account_id:
        print(f"❌ AWS account mismatch: Expected {expected_account_id} but got {actual_account_id}.")
        print("Please ensure you are using the correct AWS credentials.")
        exit(1)

    print(f"✅ AWS account verified: {actual_account_id} matches {expected_account_id}")
