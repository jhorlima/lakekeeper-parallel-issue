import typer
from pathlib import Path
from .ingestion import ingest_data

app = typer.Typer(help="Lakekeeper Iceberg Ingestion Tool")


@app.command()
def ingest(
    file_path: str = typer.Argument(
        ...,
        help="Path to the data file to ingest",
    ),
    workers: int = typer.Option(2, help="Number of parallel workers"),
    chunk_size: int = typer.Option(1000, help="Number of rows per chunk"),
):
    if not Path(file_path).exists():
        print(f"Error: File {file_path} does not exist")
        raise typer.Exit(1)

    print(f"Starting ingestion of {file_path}")

    success = ingest_data(file_path, workers, chunk_size)

    if success:
        print("All chunks ingested successfully!")
    else:
        print("Some chunks failed to ingest")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
