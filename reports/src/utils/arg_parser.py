#!/usr/bin/env python
"""
Command line argument parser
"""

import argparse

def create_parser():
    """
    Create and configure argument parser
    
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(description='Execute Athena queries with environment configuration')
    parser.add_argument('--env-file', '-e', default='.env', help='Path to environment file (default: .env)')
    
    return parser


def parse_args():
    """
    Parse command line arguments using the configured parser
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = create_parser()
    return parser.parse_args()
