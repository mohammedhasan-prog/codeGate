import click
from rich.console import Console
from rich.prompt import Prompt
import asyncio
import time
import aiofiles
from pathlib import Path

from ..core.preprocessor import CodePreprocessor
from ..core.gemini_analyzer import GeminiSecurityAnalyzer
from ..core.risk_engine import RiskEngine
from ..core.report_generator import SecurityReportGenerator

console = Console()

async def process_code(code: str, file_path: str = None):
    start_time = time.time()
    
    preprocessor = CodePreprocessor(code, file_path)
    processed_data = await preprocessor.process()

    if processed_data["language"] != "python":
        console.print(f"[yellow]Warning: Language detected as '{processed_data['language']}'. Analysis may be inaccurate.[/yellow]")

    try:
        analyzer = GeminiSecurityAnalyzer()
        gemini_result = await analyzer.analyze(processed_data["normalized_code"])
        
        risk_engine = RiskEngine(gemini_result, processed_data["total_lines"])
        
        scan_duration = time.time() - start_time
        
        report = risk_engine.create_report(
            language=processed_data["language"],
            file_path=file_path,
            scan_duration=scan_duration
        )
        
        report_generator = SecurityReportGenerator(report)
        report_generator.display()

    except Exception as e:
        console.print(f"[bold red]An error occurred during analysis: {e}[/bold red]")
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
def history():
    """Show scan history (Not implemented yet)."""
    console.print("[yellow]History feature is not yet implemented.[/yellow]")


cli.add_command(scan)
cli.add_command(paste)
cli.add_command(history)
