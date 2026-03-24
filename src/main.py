#!/usr/bin/env python3

import os
import sys
import git
import requests
import json
from datetime import datetime
from typing import List, Dict

class GitSentinel:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.repo = git.Repo(repo_path)
        self.vulns_cache = {}

    def scan_dependencies(self) -> List[Dict]:
        """Scan repository for package dependencies and known vulnerabilities"""
        dependencies = []

        # Check Python requirements.txt
        req_file = os.path.join(self.repo_path, 'requirements.txt')
        if os.path.exists(req_file):
            with open(req_file) as f:
                for line in f:
                    pkg = line.strip().split('==')[0]
                    dependencies.append({
                        'name': pkg,
                        'type': 'python'
                    })

        return self._check_vulnerabilities(dependencies)

    def _check_vulnerabilities(self, dependencies: List[Dict]) -> List[Dict]:
        """Check dependencies against vulnerability databases"""
        findings = []

        for dep in dependencies:
            if dep['name'] in self.vulns_cache:
                findings.extend(self.vulns_cache[dep['name']])
                continue

            # Query OSV database for vulnerabilities
            try:
                response = requests.get(
                    f'https://api.osv.dev/v1/query?package.name={dep["name"]}')
                vulns = response.json().get('vulns', [])
                
                if vulns:
                    self.vulns_cache[dep['name']] = vulns
                    findings.extend(vulns)
            except Exception as e:
                print(f"Error checking {dep['name']}: {str(e)}")

        return findings

    def generate_report(self, findings: List[Dict]) -> str:
        """Generate security report from findings"""
        report = ["# Security Scan Report"]
        report.append(f"\
Scan Date: {datetime.now().isoformat()}\
")

        if not findings:
            report.append("\
No security vulnerabilities found.")
        else:
            report.append(f"\
Found {len(findings)} potential security issues:\
")
            for vuln in findings:
                report.append(f"- {vuln.get('package', 'Unknown')}:")
                report.append(f"  ID: {vuln.get('id', 'N/A')}")
                report.append(f"  Severity: {vuln.get('severity', 'Unknown')}")
                report.append(f"  Details: {vuln.get('details', 'No details available')}\
")

        return '\
'.join(report)

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <repo_path>")
        sys.exit(1)

    repo_path = sys.argv[1]
    sentinel = GitSentinel(repo_path)

    print("Scanning repository for security vulnerabilities...")
    findings = sentinel.scan_dependencies()
    
    report = sentinel.generate_report(findings)
    report_path = os.path.join(repo_path, 'security_report.md')
    
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"\
Scan complete! Report saved to {report_path}")

if __name__ == '__main__':
    main()