import cv2
from flask import Flask, Response, render_template_string
from live_data import live_metrics

processed_frame = None

def generate_frames():

    global processed_frame

    while True:

        if processed_frame is None:
            continue

        ret, buffer = cv2.imencode(".jpg", processed_frame)

        frame = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n'
            + frame +
            b'\r\n'
        )


def start_dashboard(html):

    app = Flask(__name__)

    @app.route("/video_feed")
    def video_feed():

        return Response(
            generate_frames(),
            mimetype="multipart/x-mixed-replace; boundary=frame"
        )

    @app.route("/")
    def home():

        data = {
            "total_visits": live_metrics["visitors"],
            "current_occupancy": live_metrics["occupancy"],
            "peak_hour": live_metrics["peak_hour"],
            "avg_dwell": round(live_metrics["avg_dwell"], 1),
            "risk_score": round(live_metrics["risk_score"], 1),

            "recommendation": live_metrics.get(
            "recommendation",
            ["🟢 Store operations look healthy."]
            ),

            "top_visitors": live_metrics.get("top_visitors", []),

            "zones": live_metrics.get("zones", {})
        }

        return render_template_string(
            html,
            data=data
        )

    app.run(
    host="127.0.0.1",
    port=5000,
    debug=True,
    use_reloader=False
    )