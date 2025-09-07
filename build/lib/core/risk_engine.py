from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

SEVERITY_WEIGHTS = {
    "low": 1,
    "medium": 3,
    "high": 7,
    "critical": 12,
}

@dataclass
class Finding:
    tool: str = "gemini"
    vulnerability_type: str
    severity: str
    line_number: int
    code_snippet: str
    description: str
    impact: str
    remediation: str
    cwe_id: Optional[str] = None

@dataclass
class SecurityReport:
    language: str
    analysis_timestamp: datetime
    file_path: Optional[str]
    risk_score: int
    summary: str
    vulnerabilities: List[Finding]
    dependencies_analysis: dict
    total_lines: int
    scan_duration: float

class RiskEngine:
    def __init__(self, gemini_findings: dict, total_lines: int):
        self.findings = gemini_findings
        self.total_lines = total_lines

    def compute_risk_score(self) -> int:
        if not self.findings.get("vulnerabilities"):
            return 0

        total_weighted_severity = sum(
            SEVERITY_WEIGHTS.get(v.get("severity", "low").lower(), 1)
            for v in self.findings["vulnerabilities"]
        )
        
        # Normalize score based on number of vulnerabilities and code size
        # This is a simple heuristic and can be improved
        num_vulnerabilities = len(self.findings["vulnerabilities"])
        density_factor = (num_vulnerabilities / self.total_lines) * 100 if self.total_lines > 0 else 0
        
        raw_score = total_weighted_severity + density_factor
        
        # Clamp score to 0-100
        return min(100, int(raw_score))

    def create_report(self, language: str, file_path: Optional[str], scan_duration: float) -> SecurityReport:
        risk_score = self.compute_risk_score()
        
        findings_list = [
            Finding(
                vulnerability_type=v.get("type"),
                severity=v.get("severity"),
                line_number=v.get("line_number"),
                code_snippet=v.get("code_snippet"),
                description=v.get("description"),
                impact=v.get("impact"),
                remediation=v.get("remediation"),
                cwe_id=v.get("cwe_id")
            ) for v in self.findings.get("vulnerabilities", [])
        ]

        return SecurityReport(
            language=language,
            analysis_timestamp=datetime.now(),
            file_path=file_path,
            risk_score=risk_score,
            summary=self.findings.get("analysis_summary", "No summary provided."),
            vulnerabilities=findings_list,
            dependencies_analysis=self.findings.get("dependencies_analysis", {}),
            total_lines=self.total_lines,
            scan_duration=scan_duration
        )
