import typer
import subprocess
from app.db.session import Base, engine
from app.services.bayesian.train_team_strength import (
    load_historical_data,
    train_poisson_model,
    export_posteriors,
)
from app.services.predictions.generate_predictions import (
    generate_predictions_from_features,
)
from app.workers.predict_worker import run_prediction_loop

app = typer.Typer(help="Sports Analytics MVP CLI")


@app.command("init-db")
def init_db():
    """
    Initialize the database, creating all tables.
    """
    typer.echo("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    typer.echo("Database tables created successfully. ✅")


@app.command("train-bayes")
def train_bayes():
    """
    Run the Bayesian training job using historical data.
    """
    typer.echo("Starting Bayesian model training... 🧠")
    df = load_historical_data()
    typer.echo(f"Loaded {len(df)} historical matches.")

    idata, teams = train_poisson_model(df)
    typer.echo("Training completed. Exporting posteriors... 🗄️")

    export_posteriors(idata, teams)
    typer.echo("Posteriors successfully exported to the database. ✅")


@app.command("predict")
def generate_predictions():
    """
    Generate predictions based on feature snapshots.
    """
    typer.echo("Generating predictions from feature snapshots... 📊")
    generate_predictions_from_features()
    typer.echo("Predictions generated successfully. ✅")


@app.command("run-api")
def run_api(port: int = 8000, host: str = "0.0.0.0"):
    """
    Run the FastAPI application.
    """
    typer.echo(f"Starting FastAPI server at {host}:{port}... 🚀")
    subprocess.run(["uvicorn", "app.api.main:app", "--host", host, "--port", str(port)])


@app.command("run-worker")
def run_worker():
    """
    Start the background prediction and signal loop.
    """
    typer.echo("Starting the prediction and signal worker... 🤖")
    try:
        run_prediction_loop()
    except KeyboardInterrupt:
        typer.echo("\nWorker stopped gracefully. 👋")


if __name__ == "__main__":
    app()
