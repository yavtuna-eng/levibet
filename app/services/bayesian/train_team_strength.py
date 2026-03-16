import pymc as pm
import numpy as np
import pandas as pd
from datetime import datetime
from app.db.session import SessionLocal
from app.db.models import BayesianTeamStrength


def load_historical_data():
    # Mock data, normally you'd fetch from your tables
    return pd.DataFrame(
        {
            "home_team": ["TeamA", "TeamB", "TeamC"],
            "away_team": ["TeamB", "TeamC", "TeamA"],
            "home_goals": [2, 1, 0],
            "away_goals": [1, 1, 3],
        }
    )


def train_poisson_model(df):
    teams = np.unique(df[["home_team", "away_team"]].values)
    n_teams = len(teams)

    team_idx = {team: i for i, team in enumerate(teams)}
    df["home_idx"] = df["home_team"].map(team_idx)
    df["away_idx"] = df["away_team"].map(team_idx)

    with pm.Model():
        # Priors
        home_adv = pm.Normal("home_adv", mu=0, sigma=1)
        intercept = pm.Normal("intercept", mu=0, sigma=1)

        # Latent team strengths
        attack = pm.Normal("attack", mu=0, sigma=1, shape=n_teams)
        defense = pm.Normal("defense", mu=0, sigma=1, shape=n_teams)

        # Rates
        home_theta = pm.math.exp(
            intercept
            + home_adv
            + attack[df["home_idx"].values]
            - defense[df["away_idx"].values]
        )
        away_theta = pm.math.exp(
            intercept + attack[df["away_idx"].values] - defense[df["home_idx"].values]
        )

        # Likelihood
        pm.Poisson("home_goals", mu=home_theta, observed=df["home_goals"].values)
        pm.Poisson("away_goals", mu=away_theta, observed=df["away_goals"].values)

        # Sample
        idata = pm.sample(draws=500, tune=500, cores=1, progressbar=False)

    return idata, teams


def export_posteriors(idata, teams):
    db = SessionLocal()
    try:
        att_samples = idata.posterior["attack"].values.reshape(-1, len(teams))
        def_samples = idata.posterior["defense"].values.reshape(-1, len(teams))
        ha_samples = idata.posterior["home_adv"].values.flatten()

        as_of = datetime.utcnow()
        for i, team in enumerate(teams):
            strength = BayesianTeamStrength(
                team_name=team,
                league="Demo League",
                as_of=as_of,
                model_version="pymc_poisson_v1",
                attack_mean=float(att_samples[:, i].mean()),
                attack_std=float(att_samples[:, i].std()),
                defense_mean=float(def_samples[:, i].mean()),
                defense_std=float(def_samples[:, i].std()),
                home_adv_mean=float(ha_samples.mean()),
                sample_size=len(att_samples),
            )
            db.add(strength)
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    df = load_historical_data()
    idata, teams = train_poisson_model(df)
    export_posteriors(idata, teams)
    print("Bayesian Team Strength calculated and exported to DB.")
