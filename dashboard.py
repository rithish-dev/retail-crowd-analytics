from flask import Flask, render_template_string
from dashboard_data import get_latest_summary
from flask import Response
import cv2



app = Flask(__name__)
camera = cv2.VideoCapture(0) 


HTML = """
<!DOCTYPE html>

<html>

<head>

<title>Pluto Dashboard</title>

<style>

body{
background:#111827;
font-family:Arial;
color:white;
padding:40px;
}

.card{
background:#1f2937;
padding:20px;
margin:15px;
border-radius:12px;
display:inline-block;
width:220px;
text-align:center;
}

.value{
font-size:38px;
font-weight:bold;
color:#4ade80;
margin-top:10px;
}

img{
margin-top:40px;
width:100%;
max-width:900px;
background:white;
border-radius:10px;
}

</style>

</head>

<body>

<h1>🚀 Pluto Analytics</h1>

<div class="card">
<h3>Visitors Today</h3>
<div class="value">{{data.total_visits}}</div>
</div>

<div class="card">
<h3>Peak Hour</h3>
<div class="value">{{data.peak_hour}}</div>
</div>

<div class="card">
<h3>Average Dwell</h3>
<div class="value">{{data.avg_dwell}} s</div>
</div>

<div class="card">
<h3>Risk Score</h3>
<div class="value">{{data.risk_score}}</div>
</div>

<br><br>

<h2>Live Store Camera</h2>

<img src="/video_feed" style="width:900px;border-radius:12px;">

<br><br>

<h2>Hourly Visitors</h2>

<img src="/static/hourly_visitors.png" style="width:900px;">

</body>

</html>
"""




def generate_frames():

    while True:

        success, frame = camera.read()

        if not success:
            break

        ret, buffer = cv2.imencode(".jpg", frame)

        frame = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame +
            b"\r\n"
        )


@app.route("/video_feed")
def video_feed():

    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/")
def home():

    data = get_latest_summary()

    return render_template_string(
        HTML,
        data=data
    )


app.run(debug=True)