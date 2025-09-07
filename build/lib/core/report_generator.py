from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown
from .risk_engine import SecurityReport

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
            self._display_vulnerabilities()
        self._display_dependencies()
        self.console.print(f"[dim]Scan completed in {self.report.scan_duration:.2f} seconds.[/dim]")

    def _display_summary(self):
        risk_color = self._get_risk_color(self.report.risk_score)
        
        summary_panel = Panel(
            f"[bold]File:[/bold] {self.report.file_path or 'Pasted Code'}\n"
            f"[bold]Risk Score:[/bold] [{risk_color}]{self.report.risk_score}/100\n"
            f"[bold]Summary:[/bold] {self.report.summary}",
            title="[bold cyan]Security Analysis Report[/bold cyan]",
            border_style="cyan"
        )
        self.console.print(summary_panel)

    def _display_vulnerabilities(self):
        table = Table(title="[bold magenta]Vulnerabilities Detected[/bold magenta]")
        table.add_column("Severity", style="bold")
        table.add_column("Line", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Description")

        for finding in sorted(self.report.vulnerabilities, key=lambda v: v.line_number):
            color = self._get_severity_color(finding.severity)
            table.add_row(
                f"[{color}]{finding.severity.upper()}[/{color}]",
                str(finding.line_number),
                finding.vulnerability_type,
                finding.description
            )
        
        self.console.print(table)

        for finding in self.report.vulnerabilities:
            self._display_finding_details(finding)

    def _display_finding_details(self, finding):
        color = self._get_severity_color(finding.severity)
        
        details_panel = Panel(
            f"[bold]Impact:[/bold]\n{finding.impact}\n\n"
            f"[bold]Remediation:[/bold]\n{Markdown(finding.remediation)}",
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

    def _get_risk_color(self, score: int) -> str:
        if score >= 80:
            return "bold red"
        if score >= 60:
            return "red"
        if score >= 40:
            return "yellow"
        return "green"
