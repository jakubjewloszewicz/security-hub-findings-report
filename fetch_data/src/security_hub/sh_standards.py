import src.utils.aws.security_hub as security_hub
from src.utils import yaml_utils


def fetch_security_hub_standards(profile, region):
    """Fetch and save all Security Hub standards."""
    print("\n🔬 Security Hub - Standards\n")

    all_standards = security_hub.fetch_all_security_hub_standards(profile, region)
    print(f"\n📊 All Security Hub Standards: {len(all_standards)}\n")
    for s in all_standards:
        print(f"{s['Name']}")
    
    enabled_standards = security_hub.fetch_enabled_standards(profile, region)
    print(f"\n📊 Enabled Security Hub Standards: {len(enabled_standards)}\n")
    
    save_enhanced_security_hub_standards()
    
    print("\n" + "="*80)

def save_enhanced_security_hub_standards() -> list:
    
    all_standards = yaml_utils.read_file_yaml("sh_standards/all.yaml")
    enabled_standards = yaml_utils.read_file_yaml("sh_standards/enabled.yaml")
        
    # merge fields from enabled_standards into all_standards using StandardsArn, but keep all entries from all_standards
    standards = []
    for std in all_standards:
        merged_std = std.copy()
        for en_std in enabled_standards:
            if std['StandardsArn'] == en_std['StandardsArn']:
                merged_std = {**std, **en_std}
                merged_std['Enabled'] = True
                break
        standards.append(merged_std)
        
    # if std is not in enabled_standards, add Enabled: False
    for std in standards:
        if 'Enabled' not in std:
            std['Enabled'] = False

    yaml_utils.save_data_yaml(standards, "sh_standards/all_with_enabled.yaml")
    
    enabled_standards = [std for std in standards if std.get('Enabled', False)]
    
    yaml_utils.save_data_yaml(enabled_standards, "sh_standards/enabled.yaml")
    
    return standards