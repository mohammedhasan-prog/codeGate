from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.text import Text
from .risk_engine import SecurityReport
from collections import defaultdict

class SecurityReportGenerator:
    def __init__(self, report: SecurityReport):
        self.report = report
        self.console = Console()

    def _get_severity_color(self, severity: str) -> str:
        return {
            "critical": "bold red",
            "high": "red",
            "medium": "yellow",
            "low": "green",
        }.get(severity.lower(), "white")

    def display(self):
        self._display_summary()
        if self.report.vulnerabilities:
            self._display_vulnerabilities_by_type()
        self._display_dependencies()
        self._display_static_analysis_summary()
        self.console.print(f"[dim]Scan completed in {self.report.scan_duration:.2f} seconds.[/dim]")

    def _display_vulnerabilities_by_type(self):
        """Display vulnerabilities grouped by issue type."""
        # Group findings by issue type
        findings_by_type = defaultdict(list)
        for finding in self.report.vulnerabilities:
            issue_type = getattr(finding, 'issue_type', 'security')
            findings_by_type[issue_type].append(finding)
        
        # Display each group
        for issue_type in ['security', 'logic', 'performance', 'relevance', 'complexity']:
            if issue_type in findings_by_type:
                self._display_issue_group(issue_type, findings_by_type[issue_type])
    
    def _display_issue_group(self, issue_type: str, findings: list):
        """Display a group of issues of the same type."""
        # Choose appropriate styling for each issue type
        type_styles = {
            'security': {'color': 'red', 'icon': '🔒', 'title': 'Security Vulnerabilities'},
            'logic': {'color': 'yellow', 'icon': '⚠️', 'title': 'Logic Issues'},
            'performance': {'color': 'orange', 'icon': '⚡', 'title': 'Performance Issues'},
            'relevance': {'color': 'blue', 'icon': '🧹', 'title': 'Code Quality Issues'},
            'complexity': {'color': 'purple', 'icon': '📊', 'title': 'Complexity Issues'}
        }
        
        style = type_styles.get(issue_type, type_styles['security'])
        
        table = Table(title=f"[bold {style['color']}]{style['icon']} {style['title']} Detected[/bold {style['color']}]")
        table.add_column("Severity", style="bold")
        table.add_column("Line", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Description")
        
        # Add metric column for complexity issues
        if issue_type == 'complexity':
            table.add_column("Metric", style="magenta")
        
        for finding in sorted(findings, key=lambda f: f.line_number):
            color = self._get_severity_color(finding.severity)
            
            row_data = [
                f"[{color}]{finding.severity.upper()}[/{color}]",
                str(finding.line_number),
                finding.vulnerability_type,
                finding.description
            ]
            
            if issue_type == 'complexity' and hasattr(finding, 'metric_value') and finding.metric_value:
                row_data.append(f"{finding.metric_value:.1f}")
            elif issue_type == 'complexity':
                row_data.append("N/A")
            
            table.add_row(*row_data)
        
        self.console.print(table)
        
        # Display detailed findings for this group
    def _display_summary(self):
        risk_color = self._get_risk_color(self.report.risk_score)
        
        # Count issues by type
        issue_counts = defaultdict(int)
        for finding in self.report.vulnerabilities:
            issue_type = getattr(finding, 'issue_type', 'security')
            issue_counts[issue_type] += 1
        
        # Build summary text
        summary_parts = []
        if issue_counts['security'] > 0:
            summary_parts.append(f"🔒 {issue_counts['security']} security")
        if issue_counts['logic'] > 0:
            summary_parts.append(f"⚠️ {issue_counts['logic']} logic")
        if issue_counts['performance'] > 0:
            summary_parts.append(f"⚡ {issue_counts['performance']} performance")
        if issue_counts['relevance'] > 0:
            summary_parts.append(f"🧹 {issue_counts['relevance']} quality")
        if issue_counts['complexity'] > 0:
            summary_parts.append(f"📊 {issue_counts['complexity']} complexity")
        
        issues_summary = ", ".join(summary_parts) if summary_parts else "No issues found"
        
        summary_panel = Panel(
            f"[bold]File:[/bold] {self.report.file_path or 'Pasted Code'}\n"
            f"[bold]Risk Score:[/bold] [{risk_color}]{self.report.risk_score}/100[/{risk_color}]\n"
            f"[bold]Issues Found:[/bold] {issues_summary}\n"
            f"[bold]Analysis Summary:[/bold] {self.report.summary}",
            title="[bold cyan]Code Analysis Report[/bold cyan]",
            border_style="cyan"
        )
        self.console.print(summary_panel)

    def _display_finding_details(self, finding):
        color = self._get_severity_color(finding.severity)
        
        details_panel = Panel(
            f"[bold]Impact:[/bold]\n{finding.impact}\n\n"
            f"[bold]Remediation:[/bold]\n{finding.remediation}",
            title=f"[{color}]Details for Vulnerability at Line {finding.line_number}[/{color}]",
            border_style=color,
            subtitle=f"[dim]CWE: {finding.cwe_id or 'N/A'}[/dim]"
        )
        
        code_snippet = Syntax(finding.code_snippet, "python", theme="monokai", line_numbers=False)
        
        self.console.print(details_panel)
        self.console.print(code_snippet)

    def _display_dependencies(self):
        deps = self.report.dependencies_analysis
        if not deps or not deps.get("detected_imports"):
            return
            
        notes = deps.get("security_notes", "No specific notes.")
        
        dep_panel = Panel(
            f"[bold]Detected Imports:[/bold] {', '.join(deps['detected_imports'])}\n"
            f"[bold]Security Notes:[/bold] {notes}",
            title="[bold yellow]Dependency Analysis[/bold yellow]",
            border_style="yellow"
        )
        self.console.print(dep_panel)

    def _display_static_analysis_summary(self):
        """Display static analysis summary if available."""
        if not hasattr(self.report, 'static_analysis_summary') or not self.report.static_analysis_summary:
            return
        
        static_summary = self.report.static_analysis_summary
        if static_summary.get('total_issues', 0) == 0:
            return
        
        # Create summary text
        by_type = static_summary.get('by_type', {})
        by_severity = static_summary.get('by_severity', {})
        
        type_text = []
        for issue_type, count in by_type.items():
            type_text.append(f"{issue_type}: {count}")
        
        severity_text = []
        for severity, count in by_severity.items():
            color = self._get_severity_color(severity)
            severity_text.append(f"[{color}]{severity}: {count}[/{color}]")
        
        summary_panel = Panel(
            f"[bold]Total Static Analysis Issues:[/bold] {static_summary['total_issues']}\n"
            f"[bold]By Type:[/bold] {', '.join(type_text)}\n"
            f"[bold]By Severity:[/bold] {', '.join(severity_text)}",
            title="[bold yellow]📊 Static Analysis Summary[/bold yellow]",
            border_style="yellow"
        )
        self.console.print(summary_panel)

    def _get_risk_color(self, score: int) -> str:
        if score >= 80:
            return "bold red"
        if score >= 60:
            return "red"
        if score >= 40:
            return "yellow"
        return "green"
