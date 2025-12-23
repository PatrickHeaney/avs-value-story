import typer
import yaml
import asyncio
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from pydantic import ValidationError
from .parser import parse_markdown_story
from .models import ValueStory
from .runner import run_ollama_story

app = typer.Typer()
console = Console()

@app.command()
def validate(path: Path):
    content = path.read_text()
    raw_data = parse_markdown_story(content)
    try:
        story = ValueStory(**raw_data)
        console.print(Panel(f"[green]✓ {story.story_id} is Legible![/green]", border_style="green"))
    except ValidationError as e:
        console.print(f"[red]Validation Error:[/red] {e}")

@app.command()
def assemble(path: Path, output: Optional[Path] = None):
    content = path.read_text()
    raw_data = parse_markdown_story(content)
    story = ValueStory(**raw_data)
    yaml_out = yaml.dump(story.model_dump(), sort_keys=False)
    out_path = output or path.with_suffix(".yaml")
    out_path.write_text(yaml_out)
    console.print(f"[green]Assembled: {out_path}[/green]")
    return out_path

@app.command()
def run(path: Path, local: bool = False, model: str = "llama3"):
    assembled_path = assemble(path)
    if local:
        asyncio.run(run_ollama_story(str(assembled_path), model))
    else:
        console.print("[yellow]Cloud runner not implemented yet.[/yellow]")

if __name__ == "__main__":
    app()
