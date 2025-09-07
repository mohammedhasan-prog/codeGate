import unittest
from unittest.mock import patch, MagicMock
from ..core.risk_engine import RiskEngine, Finding, SecurityReport

class TestRiskEngine(unittest.TestCase):

    def setUp(self):
        self.gemini_findings = {
            "analysis_summary": "Test summary",
            "vulnerabilities": [
                {
                    "type": "sql_injection",
                    "severity": "high",
                    "line_number": 10,
                    "code_snippet": "db.execute(f\"SELECT * FROM users WHERE name = '{name}'\")",
                    "description": "SQL injection vulnerability",
                    "impact": "Data exfiltration",
                    "remediation": "Use parameterized queries.",
                    "cwe_id": "CWE-89"
                },
                {
                    "type": "command_injection",
                    "severity": "critical",
                    "line_number": 25,
                    "code_snippet": "os.system(f'ping {host}')",
                    "description": "Command injection vulnerability",
                    "impact": "Arbitrary command execution",
                    "remediation": "Avoid shell=True and sanitize input.",
                    "cwe_id": "CWE-78"
                }
            ],
            "dependencies_analysis": {
                "detected_imports": ["os", "sqlite3"],
                "security_notes": "Standard libraries."
            }
        }
        self.total_lines = 100

    def test_compute_risk_score(self):
        engine = RiskEngine(self.gemini_findings, self.total_lines)
        score = engine.compute_risk_score()
        # high (7) + critical (12) + density (2/100 * 100 = 2) = 21
        self.assertEqual(score, 21)

    def test_create_report(self):
        engine = RiskEngine(self.gemini_findings, self.total_lines)
        report = engine.create_report("python", "/path/to/test.py", 1.23)

        self.assertIsInstance(report, SecurityReport)
        self.assertEqual(report.risk_score, 21)
        self.assertEqual(len(report.vulnerabilities), 2)
        self.assertIsInstance(report.vulnerabilities[0], Finding)
        self.assertEqual(report.vulnerabilities[0].severity, "high")

if __name__ == '__main__':
    unittest.main()
