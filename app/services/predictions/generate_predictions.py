from datetime import datetime
import json
from app.db.session import SessionLocal
from app.db.models import FeatureSnapshot, Prediction


def generate_predictions_from_features():
    db = SessionLocal()
    try:
        # Just an example. In real app, query unpredicted matches with features
        snapshots = (
            db.query(FeatureSnapshot)
            .order_by(FeatureSnapshot.as_of.desc())
            .limit(50)
            .all()
        )

        for snap in snapshots:
            feats = (
                snap.features
                if isinstance(snap.features, dict)
                else json.loads(snap.features)
            )

            # Simple meta model utilizing bayesian features
            h_att = feats.get("home_attack_mean", 0)
            a_def = feats.get("away_defense_mean", 0)
            strength_diff = h_att - a_def

            h_prob = min(max(0.3 + (strength_diff * 0.1), 0.05), 0.9)
            a_prob = min(max(0.3 - (strength_diff * 0.1), 0.05), 0.9)
            d_prob = 1.0 - h_prob - a_prob

            pred = Prediction(
                match_id=snap.match_id,
                model_version="light_meta_v1",
                as_of=datetime.utcnow(),
                home_win_prob=h_prob,
                draw_prob=d_prob,
                away_win_prob=a_prob,
                confidence_score=abs(h_prob - a_prob),
                edge_score=0.05,  # Mock
            )
            db.add(pred)
            print(f"Prediction generated for match: {snap.match_id}")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    generate_predictions_from_features()
