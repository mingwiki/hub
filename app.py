import subprocess

import typer

app = typer.Typer()


@app.command()
def dev():
    """Start both backend and frontend in dev mode."""
    typer.echo("Starting development servers...")

    try:
        subprocess.Popen(["uvicorn", "main:app", "--reload"], cwd="api")
        subprocess.Popen(["pnpm", "dev"], cwd="web")
    except KeyboardInterrupt:
        typer.echo("Backend stopped.")


@app.command()
def build():
    """Build frontend for production."""
    typer.echo("Building frontend...")
    try:
        subprocess.run(["pnpm", "build"], cwd="web")
    except KeyboardInterrupt:
        typer.echo("Frontend build interrupted.")


@app.command()
def run():
    """Run backend with built frontend."""
    typer.echo("Running production server...")
    try:
        subprocess.run(["uvicorn", "main:app", "--port", "9999"], cwd="api")
    except KeyboardInterrupt:
        typer.echo("Production server stopped.")


if __name__ == "__main__":
    app()
