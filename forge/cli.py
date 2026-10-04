import sys

from rich.console import Console

from .agent import Agent


console = Console()


def main():
    console.print("[bold green]Starting Forge...[/bold green]")

    if len(sys.argv) < 3 or sys.argv[1] != "--model":
        console.print(
            "[bold]Usage:[/bold] python -m forge.cli --model MODEL"
        )
        return

    model = sys.argv[2]
    console.print(f"MODEL RAW: {model!r}")
    console.print(f"MODEL LENGTH: {len(model)}")

    console.print(f"[dim]Connecting to Ollama with model: {model}[/dim]")

    try:
        agent = Agent(model)
    except Exception as e:
        console.print(f"[red]Failed to initialize agent:[/red] {e}")
        return

    console.print("[bold green]Forge is ready.[/bold green]")
    console.print("Type 'exit' to quit.\n")

    while True:
        try:
            task = console.input("[bold cyan]forge › [/bold cyan]")
        except KeyboardInterrupt:
            console.print("\nGoodbye.")
            break

        if task.lower() in {"exit", "quit"}:
            break

        if not task.strip():
            continue

        try:
            result = agent.run(task)
            console.print(f"\n{result}\n")
        except Exception as e:
            console.print(f"[red]Agent error:[/red] {e}")


if __name__ == "__main__":
    main()