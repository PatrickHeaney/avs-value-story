import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

async def run_ollama_story(assembled_path: str, model: str = "llama3"):
    with open(assembled_path, 'r') as f:
        story_data = f.read()

    prompt = f"Execute this AVS Value Story YAML:\n\n{story_data}"
    url = "http://localhost:11434/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(description=f"Local Agent ({model}) is thinking...", total=None)
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(url, json=payload)
                result = response.json()
                console.print("\n[bold green]Product Generated Locally:[/bold green]")
                console.print(result.get("response", ""))
            except Exception as e:
                console.print(f"[red]Execution Error:[/red] {str(e)}")
