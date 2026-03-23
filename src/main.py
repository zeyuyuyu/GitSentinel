import os
import git
import torch
from transformers import CodeBertForSequenceClassification
from .analyzers import SecurityAnalyzer, BugPredictor, TechnicalDebtAnalyzer

class Scanner:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.repo = git.Repo(repo_path)
        self.model = CodeBertForSequenceClassification.from_pretrained('microsoft/codebert-base')
        
    def analyze(self):
        security_analyzer = SecurityAnalyzer(self.model)
        bug_predictor = BugPredictor(self.model)
        debt_analyzer = TechnicalDebtAnalyzer(self.model)
        
        results = {
            'security_risks': security_analyzer.scan(self.repo),
            'predicted_bugs': bug_predictor.analyze(self.repo),
            'technical_debt': debt_analyzer.forecast(self.repo)
        }
        
        return ScanResults(results)

class ScanResults:
    def __init__(self, results_dict):
        self.results = results_dict
    
    def get_insights(self):
        return {
            'high_priority': self._filter_critical_issues(),
            'recommendations': self._generate_recommendations(),
            'auto_fix_suggestions': self._generate_fixes()
        }