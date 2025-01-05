import logging
import traceback
import webbrowser
from pprint import pprint
from flask import Flask, Response, jsonify
from flask_cors import CORS
from threading import Timer

from .config import Config
from src.service.tautulli_metrics_service import TautulliMetricsService

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

logger.info("Starting Flask service...")
# Init Flask app
app = Flask(__name__)
CORS(app)

tautulli_metrics_service = TautulliMetricsService()


def open_browser():
    webbrowser.open("http://localhost:3113/webhook")


@app.route("/")
def home():
    return jsonify(
        {
            "name": "TRMNL Tautulli Dash",
            "description": "TRMLN Plugin for monitoring your Plex (Tautulli) metrics",
            "version": "1.0.09",
            "status": "running",
            "last_update": (
                tautulli_metrics_service.last_update.isoformat()
                if tautulli_metrics_service.last_update
                else None
            ),
            "refresh_interval": Config.REFRESH_INTERVAL,
        }
    )


@app.route("/webhook", methods=["GET"])
def trmnl_webhook():
    try:
        data = tautulli_metrics_service.get_data()
        logger.info(f"Data retrieved: {data}")

        assert Config.TRMNL_PLUGIN_UUID is not None
        return jsonify(data)

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        logger.error(traceback.format_exc())
        return Response({"success": "false"})


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("TRMNL Plugin Development Server")
    logger.info("=" * 80)
    logger.info(f"Server URL: http://localhost:{Config.HOST_PORT}")
    logger.info(f"Webhook URL: http://localhost:{Config.HOST_PORT}/webhook")
    logger.info("-" * 80)
    logger.info("Opening webhook URL in browser...")
    logger.info("Press Ctrl+C to quit")
    logger.info("=" * 80)

    # Open browser after a short delay
    Timer(1.5, open_browser).start()

    app.run(host=Config.HOST_IP, port=Config.HOST_PORT)
