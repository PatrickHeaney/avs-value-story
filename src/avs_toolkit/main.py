import typer
import yaml
import asyncio
from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from pathlib import Path
from pydantic import ValidationError
from .parser import parse_markdown_story
from .models import ValueStory
from .runner import run_ollama_story

app = typer.Typer(help="AVS Toolkit: Orchestrate Agentic Value Streams.")
console = Console()

@app.command()
def validate(path: Path):
    """Check if a Value Story meets Governance (Building Code) standards."""
    if not path.exists():
        console.print(f"[red]Error:[/red] File {path} not found.")
        raise typer.Exit(1)
        
    content = path.read_text()
    try:
        raw_data = parse_markdown_story(content)
        story = ValueStory(**raw_data)
        
        status_msg = "[green]Assembled & Ready[/green]" if story.is_assembled else "[yellow]Template/Definition Only[/yellow]"
        
        console.print(Panel(
            f"ID: [bold]{story.metadata.story_id}[/bold]\n"
            f"Status: {status_msg}\n"
            f"As a: [dim]{story.goal.as_a}[/dim]\n"
            f"Context: {len(story.context_manifest)} assets defined.",
            title="AVS Governance Pass", border_style="green"
        ))
    except ValidationError as e:
        console.print(f"\n[bold red]❌ Governance Failure in {path.name}[/bold red]")
        for error in e.errors():
            loc = " -> ".join([str(x) for x in error['loc']])
            console.print(f"  • [yellow]{loc}[/yellow]: {error['msg']}")
        raise typer.Exit(1)

@app.command()
def assemble(path: Path, output: Optional[Path] = None):
    """Inject context into a template and stamp it with an assembly date."""
    content = path.read_text()
    raw_data = parse_markdown_story(content)
    
    try:
        story = ValueStory(**raw_data)
        
        console.print(f"\n[bold blue]Assembling Context for {story.metadata.story_id}...[/bold blue]")
        
        # Step 1: Resolve and Inject Context Content
        for item in story.context_manifest:
            asset_path = Path(item.default_path)
            if asset_path.exists():
                item.content = asset_path.read_text()
                console.print(f"  [green]✓[/green] Injected: {item.default_path}")
            else:
                console.print(f"  [red]⚠[/red] Warning: {item.default_path} not found.")

        # Step 2: Apply the State Stamp (The Date)
        story.metadata.assembled_at = datetime.now().isoformat()
        story.metadata.status = "assembled"
        
        # Step 3: Save the 'Briefcase'
        # We use model_dump to ensure all Pydantic logic is preserved
        yaml_out = yaml.dump(story.model_dump(), sort_keys=False)
        out_path = output or path.parent / f"{story.metadata.story_id}-assembled.yaml"
        out_path.write_text(yaml_out)
        
        console.print(f"\n[bold green]✓ Assembly Complete[/bold green]")
        console.print(f"  Timestamp: {story.metadata.assembled_at}")
        console.print(f"  Briefcase: [bold]{out_path}[/bold]")
        return out_path
        
    except ValidationError as e:
        console.print(f"[red]Assembly aborted: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def run(path: Path, local: bool = typer.Option(False, "--local"), model: str = "llama3"):
    """Run a Value Story (Auto-assembles if necessary)."""
    content = path.read_text()
    raw_data = parse_markdown_story(content)
    
    try:
        story = ValueStory(**raw_data)
        target_path = path

        # Auto-Assembly Logic
        if not story.is_assembled:
            console.print("[yellow]Notice: Definition file detected. Auto-assembling context...[/yellow]")
            target_path = assemble(path)
        
        if local:
            asyncio.run(run_ollama_story(str(target_path), model))
        else:
            console.print("[yellow]Cloud execution not yet implemented. Use --local for Ollama.[/yellow]")
            
    except ValidationError as e:
        console.print(f"[red]Run aborted: Governance check failed.[/red]")
        raise typer.Exit(1)