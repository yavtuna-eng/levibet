import httpx
from app.core.config import settings
from app.db.models import Prediction


def send_telegram_message(text: str) -> str:
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHANNEL_ID:
        print(f"[MOCK TELEGRAM] Would send: \n{text}")
        return "mock_message_id_123"

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.TELEGRAM_CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown",
    }

    with httpx.Client() as client:
        resp = client.post(url, json=payload)
        resp.raise_for_status()
        return str(resp.json().get("result", {}).get("message_id"))


def format_prediction_signal(pred: Prediction, home_team: str, away_team: str) -> str:
    return f"""⚽ *Match:* {home_team} vs {away_team}
📊 *Model:* {pred.model_version}
🏠 *Home Win:* {pred.home_win_prob:.2f}
🤝 *Draw:* {pred.draw_prob:.2f}
🛫 *Away Win:* {pred.away_win_prob:.2f}
📈 *Confidence:* {pred.confidence_score:.2f}
🧠 *Edge:* Model found positive value."""
