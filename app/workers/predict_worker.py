import time
from app.services.predictions.generate_predictions import (
    generate_predictions_from_features,
)


def run_prediction_loop():
    print("Worker started: Prediction Loop")
    while True:
        try:
            print("Running predictions...")
            generate_predictions_from_features()
        except Exception as e:
            print(f"Error in prediction loop: {e}")

        # Sleep for a period before rerunning
        time.sleep(60)


if __name__ == "__main__":
    run_prediction_loop()
