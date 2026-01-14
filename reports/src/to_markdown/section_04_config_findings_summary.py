#!/usr/bin/env python3

import pandas as pd

from src.to_markdown.markown_printer import MarkdownPrinter
from src.utils.yaml_utils import read_file_yaml



class ConfigConformancePackDetailSection(MarkdownPrinter):
    """Generate detailed summary for a single conformance pack."""
    template_name = 'section_04_config_conformance_pack_summary.md.j2'
    
    def to_markdown(self, pack_name: str, pack_df: pd.DataFrame, *args, **kwargs):
        """Generate markdown for a single conformance pack."""
        control_status = pack_df.groupby('ConfigRuleName').agg({
            'ComplianceStatus': lambda x: 'FAILED' if (x == 'FAILED').any() else ('PASSED' if (x == 'PASSED').all() else 'NOT_AVAILABLE'),
            'SeverityLabel': 'first'
        }).reset_index()
        
        passed_controls = (control_status['ComplianceStatus'] == 'PASSED').sum()
        failed_controls = (control_status['ComplianceStatus'] == 'FAILED').sum()
        total_controls = len(control_status)
        not_available_controls = (control_status['ComplianceStatus'] == 'NOT_AVAILABLE').sum()
        
        failed_controls_list = control_status[control_status['ComplianceStatus'] == 'FAILED'][['ConfigRuleName', 'SeverityLabel', 'ComplianceStatus']].to_dict('records')
        
        failed_critical_high = control_status[(control_status['ComplianceStatus'] == 'FAILED') & (control_status['SeverityLabel'].isin(['CRITICAL', 'HIGH']))]
        failed_critical_high_list = failed_critical_high[['ConfigRuleName', 'SeverityLabel', 'ComplianceStatus']].to_dict('records')
        
        failed_chm_df = pack_df[(pack_df['ComplianceStatus'] == 'FAILED') & (pack_df['SeverityLabel'].isin(['CRITICAL', 'HIGH', 'MEDIUM']))]
        failed_chm_unique = failed_chm_df[['ConfigRuleName', 'SeverityLabel']].drop_duplicates()
        failed_critical_high_medium_list = failed_chm_unique.to_dict('records')
        
        valid_statuses = ['PASSED', 'FAILED', 'NON_COMPLIANT']
        valid_df = pack_df[pack_df['ComplianceStatus'].isin(valid_statuses)]
        compliant_resources = valid_df[valid_df['ComplianceStatus'] == 'PASSED'].shape[0]
        total_resources = valid_df.shape[0]
        compliance_score = int(round((compliant_resources / total_resources * 100))) if total_resources > 0 else 0
        
        pack_data = {
            'name': pack_name,
            'passed': passed_controls,
            'failed': failed_controls,
            'not_available': not_available_controls,
            'total': total_controls,
            'failed_controls': failed_controls_list,
            'failed_critical_high': failed_critical_high_list,
            'failed_critical_high_medium': failed_critical_high_medium_list,
            'compliant_resources': compliant_resources,
            'total_resources': total_resources,
            'compliance_score': compliance_score
        }
        
        return [self.template.render(pack_data=pack_data)]


class ConfigFindingsSummarySection(MarkdownPrinter):
    """Generate summary table of all conformance packs."""
    template_name = 'section_04_config_findings_summary.md.j2'
    
    def to_markdown(self, account_id, region_name, *args, **kwargs):
        aws_config_findings = read_file_yaml("sh_findings/all.yaml")
        aws_config_conformance_packs = read_file_yaml("config/conformance_packs.yaml")
        
        # Expand findings and extract conformance pack information
        expanded = []
        for finding in aws_config_findings:
            row = finding.copy()
            row['ConfigRuleArn'] = finding.get('ProductFields', {}).get('aws/config/ConfigRuleArn')
            row['ConfigRuleName'] = finding.get('ProductFields', {}).get('aws/config/ConfigRuleName')
            row['SeverityLabel'] = finding.get('Severity', {}).get('Label')
            row['ComplianceStatus'] = finding.get('Compliance', {}).get('Status')
            
            config_rule_name = row.get('ConfigRuleName') or ''
            conformance_pack = next((p.get('ConformancePackName', 'N/A') for p in aws_config_conformance_packs if p.get('ConformancePackId') in config_rule_name), 'N/A')
            row['ConformancePack'] = f"conformance-pack-{conformance_pack}"
            
            if conformance_pack == 'N/A':
                config_rule_arn = row.get('ConfigRuleArn')
                if config_rule_arn:
                    conformance_pack = config_rule_arn.split('/')[-2]
                    row['ConformancePack'] = f"{conformance_pack}"
                else:
                    row['ConformancePack'] = 'N/A'
            
            expanded.append(row)
        
        df = pd.DataFrame(expanded)
        
        # Generate summary table data
        summary_rows = []
        for conformance_pack in df['ConformancePack'].unique():
            if conformance_pack == 'N/A':
                continue
            
            pack_df = df[df['ConformancePack'] == conformance_pack]
            control_status = pack_df.groupby('ConfigRuleName').agg({
                'ComplianceStatus': lambda x: 'FAILED' if (x == 'FAILED').any() else ('PASSED' if (x == 'PASSED').all() else 'NOT_AVAILABLE')
            })
            
            passed_controls = (control_status['ComplianceStatus'] == 'PASSED').sum()
            failed_controls = (control_status['ComplianceStatus'] == 'FAILED').sum()
            total_controls = len(control_status)
            
            valid_statuses = ['PASSED', 'FAILED', 'NON_COMPLIANT']
            valid_df = pack_df[pack_df['ComplianceStatus'].isin(valid_statuses)]
            compliant_resources = valid_df[valid_df['ComplianceStatus'] == 'PASSED'].shape[0]
            total_resources = valid_df.shape[0]
            compliance_score = round((compliant_resources / total_resources * 100), 2) if total_resources > 0 else 0
            
            summary_rows.append({
                'pack': conformance_pack,
                'passed': passed_controls,
                'failed': failed_controls,
                'total': total_controls,
                'score': compliance_score
            })
        
        # Generate main summary section
        rendered = self.template.render(
            account_id=account_id,
            summary_rows=summary_rows
        )
        
        # Generate individual pack detail sections
        pack_summaries_md = []
        detail_generator = ConfigConformancePackDetailSection()
        for pack_name in df['ConformancePack'].unique():
            if pack_name == 'N/A':
                continue
            pack_df = df[df['ConformancePack'] == pack_name]
            pack_summaries_md.extend(detail_generator.to_markdown(pack_name, pack_df))
        
        if pack_summaries_md:
            return [rendered] + pack_summaries_md
        else:
            return [rendered]


