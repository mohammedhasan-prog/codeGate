import click
from rich.console import Console
from rich.text import Text
from .commands import cli

console = Console()

class CodeGateCLI:
    def __init__(self):
        self.prompt = Text("> ", style="bold green")

    def run(self):
        console.print("[bold cyan]Welcome to CodeGate Security Auditor![/bold cyan]")
        console.print("Type 'help' for a list of commands.")

        while True:
            try:
                command_line = console.input(self.prompt)
                if not command_line.strip():
                    continue
                
                if command_line.strip() == ':quit':
                    break
                
                if command_line.strip() == 'help':
                    self.show_help()
                    continue

                # Split command and arguments
                parts = command_line.split()
                command_name = parts[0]
                args = parts[1:]

                if command_name in cli.commands:
                    try:
                        cli.main(args=[command_name] + args, standalone_mode=False)
                    except click.exceptions.MissingParameter as e:
                        console.print(f"[yellow]Usage: {command_name} {e.param.human_readable_name}[/yellow]")
                    except click.exceptions.UsageError as e:
                        console.print(f"[red]{e.message}[/red]")
                    except SystemExit:
                        # Prevent exit from REPL
                        pass
                else:
                    console.print(f"[red]Unknown command: '{command_name}'. Type 'help' for available commands.[/red]")

            except KeyboardInterrupt:
                console.print("\n[yellow]Use :quit to exit.[/yellow]")
            except EOFError:
                break
        
        console.print("[bold cyan]Goodbye![/bold cyan]")

    def show_help(self):
        console.print("\n[bold]Available Commands:[/bold]")
        console.print("  [cyan]scan [file_path][/cyan]     - Analyze a specific Python file.")
        console.print("  [cyan]paste[/cyan]                 - Enter multi-line paste mode for code snippets.")
        console.print("  [cyan]history[/cyan]               - View recent scan history.")
        console.print("  [cyan]history --stats[/cyan]       - View scan statistics and risk distribution.")
        console.print("  [cyan]history --details <id>[/cyan] - View detailed report for a specific scan.")
        console.print("  [cyan]history --limit <n>[/cyan]   - Show last n scans (default: 20).")
        console.print("  [cyan]history --clear[/cyan]       - Clear all scan history.")
        console.print("  [cyan]help[/cyan]                  - Show this help message.")
        console.print("  [cyan]:quit[/cyan]                 - Exit the CodeGate CLI.\n")


def main():
    cli_app = CodeGateCLI()
    cli_app.run()

if __name__ == "__main__":
    main()
