from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db, engine, Base
import app.db.models as models

# Only for MVP. In production, use Alembic.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sports Analytics MVP")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/matches/upcoming")
def get_upcoming_matches(db: Session = Depends(get_db)):
    matches = (
        db.query(models.Match).order_by(models.Match.kickoff_at.asc()).limit(15).all()
    )
    return {"matches": matches}


@app.get("/predictions/latest")
def get_latest_predictions(db: Session = Depends(get_db)):
    predictions = (
        db.query(models.Prediction)
        .order_by(models.Prediction.as_of.desc())
        .limit(15)
        .all()
    )
    return {"predictions": predictions}


@app.post("/admin/train-bayes/run")
def run_bayes_training():
    # In reality you would trigger a celery task or background task here
    return {"message": "Bayesian training job triggered."}
