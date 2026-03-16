# Sports Analytics MVP 🎯

This repository contains the foundational MVP for a **Sports Analytics and Signal Dispatching Product**. The system uses a **Bayesian model** to evaluate team strengths, generates **feature snapshots**, runs prediction models, and dispatches high-confidence signals via **Telegram**.

## 🧠 Architecture Overview

The system is built with a resilient and scalable modular architecture:

1. **PostgreSQL Database**: Acts as the single source of truth. Stores raw event data, `odds_snapshots`, `feature_snapshots` (JSONB) as our lightweight Feature Store, and Bayesian `team_strengths`.
2. **Bayesian Core (PyMC)**: Processes historical data to infer latent relative strengths (attack vs. defense) of teams using Markov Chain Monte Carlo (MCMC).
3. **Prediction Engine**: Consumes snapshot features from the database to generate 1X2 market probabilities.
4. **Signal Dispatcher**: Continuously evaluates current predictions and drops insights (Telegram signals) for identified 'edges'.
5. **FastAPI Serving Layer**: Serves predictions and match data to front-end consumers or dashboard interfaces.

## 🛠️ Technology Stack

- **API:** FastAPI, Pydantic, Uvicorn
- **Database:** PostgreSQL, SQLAlchemy (ORM), Alembic
- **Machine Learning:** PyMC (Bayesian Inference), Pandas, Numpy
- **CLI/Task Execution:** Typer
- **Containerization:** Docker & Docker Compose

## 🚀 Getting Started

To spin up the entire application (API, Background Worker, and Database) out of the box:

```bash
# Start all services
docker-compose up --build
```

- **FastAPI Server** will map to `localhost:8000` (Visit `http://localhost:8000/docs` for the Swagger UI).
- **PostgreSQL Database** will map to `localhost:5432`.
- **Worker Process** will start executing continuous prediction & signal delivery loops.

---

## 💻 Working with the CLI (`cli.py`)

A Typer-based CLI is included to allow you to interactively test, manage, and debug the system without entering the Docker containers or wrestling with scripts.

Make sure you have your dependencies installed (or you are inside the Docker container) when running these:

### 1. Initialize the Database

Creates all required tables in the PostgreSQL database.

```bash
python cli.py init-db
```

### 2. Train the Bayesian Model

Loads historical data, compiles the PyMC Poisson model, runs the MCMC sampling, and writes the resulting posterior mean/std statistics into the `bayesian_team_strength` table.

```bash
python cli.py train-bayes
```

### 3. Generate Predictions manually

Fetches the latest `feature_snapshots` from the database, applies the meta-model, and writes new probable outcomes into the `predictions` table.

```bash
python cli.py predict
```

### 4. Run the API Server manually

Starts the FastAPI uvicorn daemon. Very useful for local development outside of docker-compose.

```bash
python cli.py run-api
```

### 5. Run the Background Worker manually

Starts the prediction daemon loop (the engine that continuously triggers predictions and evaluates signals for Telegram dispatch).

```bash
python cli.py run-worker
```

---

## 🗄️ Project Structure

```text
.
├── docker-compose.yml              # Architecture Services
├── Dockerfile                      # App Container definition
├── requirements.txt                # Python Dependencies
├── cli.py                          # 🛠️ Command Line Interface Controller
├── .env                            # Environment variables (DB URL, API Tokens)
└── app/
    ├── api/
    │   └── main.py                 # FastAPI endpoints
    ├── core/
    │   └── config.py               # pydantic_settings configuration
    ├── db/
    │   ├── models.py               # SQLAlchemy schema definitions
    │   └── session.py              # DB Engine & Session Makers
    ├── services/
    │   ├── bayesian/
    │   │   └── train_team_strength.py  # PyMC model compilation & training
    │   ├── predictions/
    │   │   └── generate_predictions.py # Generating inferences from features
    │   └── telegram/
    │       └── sender.py           # Signal text formatting & API client
    └── workers/
        └── predict_worker.py       # Infinite loop worker for continuous pipeline
```

## 🔒 Environment Variables

Copy the `.env` file configuration and update credentials appropriately:

```dotenv
DATABASE_URL=postgresql://sports:sports@localhost:5432/sports
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=your_channel_id_here
```

_(Note: Use `@db` as the hostname instead of `localhost` if running commands from inside the api/worker docker containers)._

## 🛑 Important Notes

- **Signals vs Bets:** This architecture generates and alerts about statistical _"edges"_ (Signals). It **does not inherently place automated bets**.
- **Feature Completeness:** To feed the MCMC pipeline, an Ingestion layer connecting to an origin such as _OddsAPI_ or _Sportradar_ is logically necessary and is intended to populate the `matches` and `odds_snapshots` tables prior to feature extraction.
