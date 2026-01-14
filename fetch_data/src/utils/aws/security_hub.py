
import boto3
import src.utils.yaml_utils as yaml_utils

def normalize_standard_id(standard_arn: str) -> str:
    """Normalize standard ID by replacing colons and slashes with underscores."""
    # Example: arn:aws:securityhub:eu-north-1::standards/cis-aws-foundations-benchmark/v/5.0.0
    parts = standard_arn.split('/')
    standard_id = parts[-3] + '_' + parts[-2] + '_' + parts[-1]
    return standard_id

def fetch_all_findings (profile, account_id, region):
    """
    Fetch all Security Hub findings for a given AWS account.
    """
    session = boto3.Session(profile_name=profile, region_name=region)
    sh = session.client('securityhub')

    print(f"🔎 Filtering findings for account: {account_id}")
    
    Filters = {
        'RecordState': [{
            'Comparison': 'EQUALS',
            'Value': 'ACTIVE',
        }],
        'AwsAccountId': [{
            'Comparison': 'EQUALS',
            'Value': account_id
        }],
    }
    
    
    all_findings = []
    next_token = None
    
    while True:
        print(f"⏳ Fetching findings... Retrieved so far: {len(all_findings)}")
        if next_token:
            response = sh.get_findings(
                Filters=Filters,
                MaxResults=100,
                NextToken=next_token
            )
        else:
            response = sh.get_findings(
                Filters=Filters,
                MaxResults=100
            )
        print(f"    ➕ Fetched: {len(response.get('Findings', []))} findings")
        
        all_findings.extend(response.get('Findings', []))
        next_token = response.get('NextToken')
        
        if not next_token:
            break

    yaml_utils.save_data_yaml(all_findings, "sh_findings/all.yaml")
    
    print(f"✅ Found {len(all_findings)} finding(s).")
    return all_findings

def fetch_all_security_hub_standards(profile, region):
    """
    Fetch Security Hub CSPM Security Standards from AWS with security scores
    """
    session = boto3.Session(profile_name=profile, region_name=region)
    sh = session.client('securityhub')
    
    print("\n📋 Fetching Security Hub CSPM Security Standards...\n")
    
    # Get all enabled standards subscriptions
    response = sh.describe_standards()
    
    standards = response.get('Standards', [])

    yaml_utils.save_data_yaml(standards, "sh_standards/all.yaml")

    if not standards:
        print("⚠️  No security standards are currently enabled.")
        return standards
    
    return standards

def fetch_enabled_standards(profile, region):
    """
    Fetch enabled Security Hub standards for a specific account
    """
    session = boto3.Session(profile_name=profile, region_name=region)
    sh = session.client('securityhub')
    
    print("\n📋 Fetching enabled Security Hub Standards...\n")
    
    # Get all enabled standards subscriptions
    response = sh.get_enabled_standards()
    
    standards = response.get('StandardsSubscriptions', [])

    yaml_utils.save_data_yaml(standards, "sh_standards/enabled.yaml")
    
    if not standards:
        print("⚠️  No security standards are currently enabled.")
        return standards
    
    return standards

def fetch_standards_controls(subscription_arn, profile, region):
    """
    Describe standards controls for a given subscription ARN
    """
    session = boto3.Session(profile_name=profile, region_name=region)
    sh = session.client('securityhub')
    
    print(f"\n📋 Describing standards controls for subscription: {subscription_arn}\n")
    
    controls = []
    next_token = None
    
    while True:
        print(f"⏳ Fetching controls... Retrieved so far: {len(controls)}")
        if next_token:
            response = sh.describe_standards_controls(
                StandardsSubscriptionArn=subscription_arn,
                MaxResults=100,
                NextToken=next_token
            )
        else:
            response = sh.describe_standards_controls(
                StandardsSubscriptionArn=subscription_arn,
                MaxResults=100
            )
        print(f"    ➕ Fetched: {len(response.get('Controls', []))} controls")
        
        controls.extend(response.get('Controls', []))
        next_token = response.get('NextToken')
        
        if not next_token:
            break
        
    standard_id = normalize_standard_id(subscription_arn)
    yaml_utils.save_data_yaml(controls, f"sh_standards/{standard_id}/controls.yaml")
    return controls
