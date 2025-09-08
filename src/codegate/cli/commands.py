import click
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import asyncio
import time
import aiofiles
from pathlib import Path
from datetime import datetime

from ..core.preprocessor import CodePreprocessor
from ..core.gemini_analyzer import GeminiSecurityAnalyzer
from ..core.static_analyzer import analyze_code_static
from ..core.risk_engine import RiskEngine
from ..core.report_generator import SecurityReportGenerator
from ..utils.history import history_manager

console = Console()

async def process_code(code: str, file_path: str = None):
    start_time = time.time()
    
    preprocessor = CodePreprocessor(code, file_path)
    processed_data = await preprocessor.process()

    if processed_data["language"] != "python":
        console.print(f"[yellow]Warning: Language detected as '{processed_data['language']}'. Analysis may be inaccurate.[/yellow]")

    try:
        # Run both security analysis (Gemini) and static analysis
        console.print("[dim]Running security analysis...[/dim]")
        analyzer = GeminiSecurityAnalyzer()
        gemini_result = await analyzer.analyze(processed_data["normalized_code"])
        
        console.print("[dim]Running static code analysis...[/dim]")
        static_issues = analyze_code_static(code)
        
        risk_engine = RiskEngine(
            gemini_findings=gemini_result, 
            total_lines=processed_data["total_lines"],
            static_findings=static_issues
        )
        
        scan_duration = time.time() - start_time
        
        report = risk_engine.create_report(
            language=processed_data["language"],
            file_path=file_path,
            scan_duration=scan_duration
        )
        
        report_generator = SecurityReportGenerator(report)
        report_generator.display()
        
        # Save scan to history
        if history_manager.is_enabled():
            report_data = {
                'file_path': report.file_path,
                'language': report.language,
                'risk_score': report.risk_score,
                'vulnerabilities': [
                    {
                        'type': v.vulnerability_type,
                        'severity': v.severity,
                        'line_number': v.line_number,
                        'code_snippet': v.code_snippet,
                        'description': v.description,
                        'impact': v.impact,
                        'remediation': v.remediation,
                        'cwe_id': v.cwe_id,
                        'tool': v.tool,
                        'issue_type': v.issue_type,
                        'category': v.category,
                        'metric_value': v.metric_value
                    } for v in report.vulnerabilities
                ],
                'summary': report.summary,
                'scan_duration': report.scan_duration,
                'analysis_timestamp': report.analysis_timestamp.isoformat(),
                'dependencies_analysis': report.dependencies_analysis,
                'total_lines': report.total_lines,
                'static_analysis_summary': report.static_analysis_summary
            }
            
            scan_id = history_manager.save_scan(report_data)
            if scan_id:
                console.print(f"[dim]Scan saved to history with ID: {scan_id}[/dim]")

    except Exception as e:
        console.print(f"[bold red]An error occurred during analysis: {e}[/bold red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
    finally:
        CodePreprocessor.cleanup_temp_file(processed_data["temp_file_path"])


@click.group()
def cli():
    """CodeGate: A Python security auditor using Gemini."""
    pass

@click.command()
@click.argument('file_path', type=click.Path(exists=True, dir_okay=False, readable=True), required=False)
def scan(file_path):
    """Analyzes a Python file for vulnerabilities."""
    if not file_path:
        console.print("[cyan]Usage: scan /path/to/file.py[/cyan]")
        return

    async def run_scan():
        try:
            async with aiofiles.open(file_path, "r") as f:
                code = await f.read()
            await process_code(code, file_path)
        except FileNotFoundError:
            console.print(f"[bold red]Error: File not found at '{file_path}'[/bold red]")
        except Exception as e:
            console.print(f"[bold red]An error occurred: {e}[/bold red]")

    asyncio.run(run_scan())


@click.command()
def paste():
    """Enter paste mode to analyze a snippet of code."""
    console.print("[cyan]Enter your code snippet below. Press Ctrl+D (or Ctrl+Z on Windows) to finish.[/cyan]")
    lines = []
    while True:
        try:
            line = input()
            lines.append(line)
        except EOFError:
            break
    code = "\n".join(lines)
    if code:
        asyncio.run(process_code(code))
    else:
        console.print("[yellow]No code provided.[/yellow]")

@click.command()
@click.option('--limit', '-l', default=20, help='Number of recent scans to show')
@click.option('--details', '-d', help='Show detailed report for specific scan ID')
@click.option('--stats', '-s', is_flag=True, help='Show scan statistics')
@click.option('--clear', is_flag=True, help='Clear all scan history')
def history(limit, details, stats, clear):
    """Show scan history and statistics."""
    
    if clear:
        confirm = Prompt.ask("[red]Are you sure you want to clear all scan history?[/red]", 
                           choices=["yes", "no"], default="no")
        if confirm == "yes":
            if history_manager.clear_history():
                console.print("[green]✓ Scan history cleared successfully.[/green]")
            else:
                console.print("[red]✗ Failed to clear scan history.[/red]")
        return
    
    if stats:
        show_statistics()
        return
    
    if details:
        show_scan_details(details)
        return
    
    show_recent_scans(limit)


def show_recent_scans(limit: int):
    """Display recent scan history."""
    entries = history_manager.get_recent_scans(limit)
    
    if not entries:
        console.print("[yellow]No scan history found.[/yellow]")
        console.print("[dim]Run some scans to build up your history![/dim]")
        return
    
    table = Table(title=f"[bold cyan]Recent Scans (Last {len(entries)})[/bold cyan]")
    table.add_column("Scan ID", style="cyan", no_wrap=True)
    table.add_column("Date/Time", style="green")
    table.add_column("File", style="blue")
    table.add_column("Risk Score", justify="center")
    table.add_column("Vulnerabilities", justify="center", style="red")
    table.add_column("Duration", justify="right", style="dim")
    
    for entry in entries:
        # Format timestamp
        timestamp = datetime.fromisoformat(entry.timestamp)
        formatted_time = timestamp.strftime("%m/%d %H:%M")
        
        # Format file path
        file_display = entry.file_path or "[italic]Pasted Code[/italic]"
        if entry.file_path and len(entry.file_path) > 30:
            file_display = "..." + entry.file_path[-27:]
        
        # Risk score color
        risk_color = get_risk_color(entry.risk_score)
        risk_display = f"[{risk_color}]{entry.risk_score}/100[/{risk_color}]"
        
        # Vulnerability count color
        vuln_color = "red" if entry.vulnerabilities_count > 0 else "green"
        vuln_display = f"[{vuln_color}]{entry.vulnerabilities_count}[/{vuln_color}]"
        
        table.add_row(
            entry.scan_id,
            formatted_time,
            file_display,
            risk_display,
            vuln_display,
            f"{entry.scan_duration:.1f}s"
        )
    
    console.print(table)
    console.print(f"\n[dim]Use --details <scan_id> to view detailed report for a specific scan[/dim]")
    console.print(f"[dim]Use --stats to view overall statistics[/dim]")


def show_scan_details(scan_id: str):
    """Show detailed information for a specific scan."""
    detailed_entry = history_manager.get_scan_details(scan_id)
    
    if not detailed_entry:
        console.print(f"[red]✗ Scan with ID '{scan_id}' not found in history.[/red]")
        return
    
    entry = detailed_entry.entry
    report_data = detailed_entry.full_report
    
    # Create a mock SecurityReport object for the report generator
    from ..core.risk_engine import SecurityReport, Finding
    
    findings = []
    for vuln in report_data.get('vulnerabilities', []):
        finding = Finding(
            vulnerability_type=vuln.get('type', ''),
            severity=vuln.get('severity', ''),
            line_number=vuln.get('line_number', 0),
            code_snippet=vuln.get('code_snippet', ''),
            description=vuln.get('description', ''),
            impact=vuln.get('impact', ''),
            remediation=vuln.get('remediation', ''),
            cwe_id=vuln.get('cwe_id')
        )
        findings.append(finding)
    
    mock_report = SecurityReport(
        language=report_data.get('language', 'unknown'),
        analysis_timestamp=datetime.fromisoformat(report_data.get('analysis_timestamp')),
        file_path=report_data.get('file_path'),
        risk_score=report_data.get('risk_score', 0),
        summary=report_data.get('summary', ''),
        vulnerabilities=findings,
        dependencies_analysis=report_data.get('dependencies_analysis', {}),
        total_lines=report_data.get('total_lines', 0),
        scan_duration=report_data.get('scan_duration', 0.0)
    )
    
    console.print(f"\n[bold cyan]═══ Historical Scan Report ═══[/bold cyan]")
    console.print(f"[bold]Scan ID:[/bold] {entry.scan_id}")
    console.print(f"[bold]Scanned on:[/bold] {datetime.fromisoformat(entry.timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
    
    report_generator = SecurityReportGenerator(mock_report)
    report_generator.display()


def show_statistics():
    """Show scan history statistics."""
    stats = history_manager.get_statistics()
    
    if stats['total_scans'] == 0:
        console.print("[yellow]No scan history available for statistics.[/yellow]")
        return
    
    # Overall stats panel
    stats_panel = Panel(
        f"[bold]Total Scans:[/bold] {stats['total_scans']}\n"
        f"[bold]Total Vulnerabilities Found:[/bold] {stats['total_vulnerabilities']}\n"
        f"[bold]Average Risk Score:[/bold] {stats['average_risk_score']}/100",
        title="[bold cyan]Scan Statistics[/bold cyan]",
        border_style="cyan"
    )
    console.print(stats_panel)
    
    # Risk distribution table
    risk_table = Table(title="[bold yellow]Risk Score Distribution[/bold yellow]")
    risk_table.add_column("Risk Level", style="bold")
    risk_table.add_column("Count", justify="center")
    risk_table.add_column("Percentage", justify="center")
    
    risk_dist = stats['risk_distribution']
    total = stats['total_scans']
    
    for level, count in risk_dist.items():
        percentage = (count / total * 100) if total > 0 else 0
        color = get_risk_level_color(level)
        risk_table.add_row(
            f"[{color}]{level.title()}[/{color}]",
            str(count),
            f"{percentage:.1f}%"
        )
    
    console.print(risk_table)


def get_risk_color(score: int) -> str:
    """Get color for risk score."""
    if score >= 75:
        return "bold red"
    elif score >= 50:
        return "red"
    elif score >= 25:
        return "yellow"
    else:
        return "green"


def get_risk_level_color(level: str) -> str:
    """Get color for risk level."""
    colors = {
        'low': 'green',
        'medium': 'yellow', 
        'high': 'red',
        'critical': 'bold red'
    }
    return colors.get(level, 'white')


cli.add_command(scan)
cli.add_command(paste)
cli.add_command(history)
