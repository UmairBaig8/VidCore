from pathlib import Path
import typer

from core.agent_loader import AgentLoader
from core.orchestrator import VideoOrchestrator

app = typer.Typer(
    help="Video Analysis Agent Platform"
)


@app.command()
def agents():
    """
    Show loaded agents
    """

    loader = AgentLoader()
    loaded = loader.load()

    typer.echo("")
    typer.echo("Loaded Agents")
    typer.echo("-------------")

    for name in loaded:
        typer.echo(f"✓ {name}")


@app.command()
def skills():
    """
    Show loaded skills
    """

    from core.registry import SkillRegistry

    registry = SkillRegistry()
    registry.load()

    typer.echo("")
    typer.echo("Loaded Skills")
    typer.echo("-------------")

    for skill in registry.skills:
        typer.echo(f"✓ {skill}")


@app.command()
def videos():
    """
    List available videos
    """

    video_dir = Path("videos")

    if not video_dir.exists():
        typer.echo("videos/ folder not found")
        raise typer.Exit()

    files = list(video_dir.glob("*"))

    if not files:
        typer.echo("No videos found")
        return

    typer.echo("")
    typer.echo("Available Videos")
    typer.echo("----------------")

    for idx, video in enumerate(files, start=1):
        typer.echo(f"{idx}. {video.name}")


@app.command()
def analyze(
    video: str,
    interval: float = typer.Option(
        0.5,
        "--interval",
        "-i",
        help="Frame sampling interval in seconds"
    ),
):
    """
    Analyze a video
    """

    video_path = Path(video)

    if not video_path.exists():
        typer.echo(f"Video not found: {video}")
        raise typer.Exit(1)

    orchestrator = VideoOrchestrator(
        video_path=str(video_path),
        sample_interval=interval
    )

    orchestrator.run()


@app.command()
def stream(
    video: str,
    interval: float = typer.Option(0.5)
):
    """
    Live event stream
    """

    video_path = Path(video)

    orchestrator = VideoOrchestrator(
        video_path=str(video_path),
        sample_interval=interval,
        stream_mode=True
    )

    orchestrator.run()


@app.command()
def report(
    video: str
):
    """
    Generate report only
    """

    orchestrator = VideoOrchestrator(
        video_path=video,
        report_only=True
    )

    orchestrator.run()


@app.command()
def doctor():
    """
    Validate environment
    """

    typer.echo("")
    typer.echo("Environment Check")
    typer.echo("-----------------")

    checks = {
        "agents": Path("agents").exists(),
        "skills": Path("skills").exists(),
        "videos": Path("videos").exists(),
        "output": Path("output").exists(),
    }

    for name, status in checks.items():
        icon = "✓" if status else "✗"
        typer.echo(f"{icon} {name}")


@app.command()
def config():
    """
    Show runtime config
    """

    from core.config import load_config

    cfg = load_config()

    typer.echo("")
    typer.echo("Configuration")
    typer.echo("-------------")

    for key, value in cfg.items():
        typer.echo(f"{key}: {value}")


if __name__ == "__main__":
    app()