from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

SEVERITY_WEIGHTS = {
    "low": 1,
    "medium": 3,
    "high": 7,
    "critical": 12,
}

@dataclass
class Finding:
    vulnerability_type: str
    severity: str
    line_number: int
    code_snippet: str
    description: str
    impact: str
    remediation: str
    tool: str = "gemini"
    cwe_id: Optional[str] = None
    issue_type: str = "security"  # "security", "logic", "performance", "relevance", "complexity"
    category: Optional[str] = None  # Subcategory for static analysis issues
    metric_value: Optional[float] = None  # For complexity metrics

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
    static_analysis_summary: Optional[Dict[str, Any]] = None

class RiskEngine:
    def __init__(self, gemini_findings: dict, total_lines: int, static_findings: List = None):
        self.findings = gemini_findings
        self.total_lines = total_lines
        self.static_findings = static_findings or []

    def compute_risk_score(self) -> int:
        security_score = self._compute_security_score()
        static_score = self._compute_static_analysis_score()
        
        # Combine scores: security issues are weighted more heavily
        combined_score = min(100, int(security_score * 0.8 + static_score * 0.2))
        return combined_score
    
    def _compute_security_score(self) -> int:
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
    
    def _compute_static_analysis_score(self) -> int:
        if not self.static_findings:
            return 0
        
        # Weight static analysis issues differently
        static_weights = {
            "logic": {"critical": 8, "high": 5, "medium": 3, "low": 1},
            "performance": {"critical": 6, "high": 4, "medium": 2, "low": 1},
            "relevance": {"critical": 4, "high": 2, "medium": 1, "low": 0.5},
            "complexity": {"critical": 5, "high": 3, "medium": 2, "low": 1}
        }
        
        total_static_score = 0
        for finding in self.static_findings:
            issue_type = getattr(finding, 'type', 'logic')
            severity = getattr(finding, 'severity', 'low')
            weight = static_weights.get(issue_type, static_weights['logic']).get(severity, 1)
            total_static_score += weight
        
        # Normalize based on code size
        density_factor = (len(self.static_findings) / self.total_lines) * 50 if self.total_lines > 0 else 0
        raw_score = total_static_score + density_factor
        
        return min(100, int(raw_score))

    def create_report(self, language: str, file_path: Optional[str], scan_duration: float) -> SecurityReport:
        risk_score = self.compute_risk_score()
        
        # Create findings list combining security and static analysis findings
        findings_list = []
        
        # Add security findings from Gemini
        for v in self.findings.get("vulnerabilities", []):
            findings_list.append(Finding(
                vulnerability_type=v.get("type"),
                severity=v.get("severity"),
                line_number=v.get("line_number"),
                code_snippet=v.get("code_snippet"),
                description=v.get("description"),
                impact=v.get("impact"),
                remediation=v.get("remediation"),
                cwe_id=v.get("cwe_id"),
                tool="gemini",
                issue_type="security"
            ))
        
        # Add static analysis findings
        for static_issue in self.static_findings:
            findings_list.append(Finding(
                vulnerability_type=static_issue.category or static_issue.type,
                severity=static_issue.severity,
                line_number=static_issue.line_number,
                code_snippet=static_issue.code_snippet,
                description=static_issue.description,
                impact=static_issue.impact,
                remediation=static_issue.remediation,
                tool="static_analyzer",
                issue_type=static_issue.type,
                category=static_issue.category,
                metric_value=static_issue.metric_value
            ))
        
        # Generate static analysis summary
        static_summary = self._generate_static_analysis_summary()
        
        # Combine summaries
        combined_summary = self.findings.get("analysis_summary", "No security analysis summary provided.")
        if static_summary["total_issues"] > 0:
            combined_summary += f" Static analysis found {static_summary['total_issues']} additional issues: {static_summary['summary']}"

        return SecurityReport(
            language=language,
            analysis_timestamp=datetime.now(),
            file_path=file_path,
            risk_score=risk_score,
            summary=combined_summary,
            vulnerabilities=findings_list,
            dependencies_analysis=self.findings.get("dependencies_analysis", {}),
            total_lines=self.total_lines,
            scan_duration=scan_duration,
            static_analysis_summary=static_summary
        )
    
    def _generate_static_analysis_summary(self) -> Dict[str, Any]:
        """Generate summary statistics for static analysis findings."""
        if not self.static_findings:
            return {"total_issues": 0, "summary": "No static analysis issues found."}
        
        # Count issues by type and severity
        type_counts = {}
        severity_counts = {}
        
        for finding in self.static_findings:
            issue_type = finding.type
            severity = finding.severity
            
            type_counts[issue_type] = type_counts.get(issue_type, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Generate summary text
        summary_parts = []
        for issue_type, count in type_counts.items():
            summary_parts.append(f"{count} {issue_type}")
        
        summary = f"{', '.join(summary_parts)} issues"
        
        return {
            "total_issues": len(self.static_findings),
            "by_type": type_counts,
            "by_severity": severity_counts,
            "summary": summary
        }
