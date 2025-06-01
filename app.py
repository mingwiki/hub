import os
import signal
import subprocess
import sys

import typer

app = typer.Typer()


@app.command()
def dev():
    """Start both backend and frontend in dev mode."""
    typer.echo("Starting development servers...")

    # Start backend and frontend in their own process groups
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "9999"],
        cwd="api",
        preexec_fn=os.setsid,  # Start the process in a new session
    )
    frontend_process = subprocess.Popen(
        ["pnpm", "dev"],
        cwd="web",
        preexec_fn=os.setsid,  # Start the process in a new session
    )

    try:
        # Wait for both processes to complete
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        typer.echo("Stopping development servers...")

        # Terminate both process groups
        os.killpg(os.getpgid(backend_process.pid), signal.SIGTERM)
        os.killpg(os.getpgid(frontend_process.pid), signal.SIGTERM)

        # Wait for processes to terminate
        backend_process.wait()
        frontend_process.wait()

        typer.echo("Development servers stopped.")


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
