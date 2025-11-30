import os
from datetime import date
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
import requests

# Load .env (PG_DSN + Adafruit IO)
load_dotenv()

PG_DSN = os.getenv("PG_DSN")
AIO_USERNAME = os.getenv("AIO_USERNAME")
AIO_KEY = os.getenv("AIO_KEY")

# Feeds
AIO_COMMAND_FEED = os.getenv("AIO_COMMAND_FEED", "picarx-command")
AIO_STEERING_FEED = os.getenv("AIO_STEERING_FEED", "steering-command")
AIO_CAMERA_FEED = os.getenv("AIO_CAMERA_FEED", "camera-command")
AIO_LINE_FEED = os.getenv("AIO_LINE_FEED", "line-command")
AIO_OBSTACLE_FEED = os.getenv("AIO_OBSTACLE_FEED", "obstacle-command")
AIO_ULTRA_HTTP_FEED = os.getenv("AIO_ULTRA_HTTP_FEED", "ultrasonic-distance")
AIO_GRAY_MID_HTTP_FEED = os.getenv("AIO_GRAY_MID_HTTP_FEED", "grayscale-mid")
AIO_TTS_FEED = os.getenv("AIO_TTS_FEED", "tts")

if not PG_DSN:
    raise RuntimeError("PG_DSN is not set in .env")

app = Flask(__name__)


def get_conn():
    return psycopg2.connect(PG_DSN, sslmode="require")


# ------------ Adafruit IO helpers ------------

def _aio_get_json(path: str, params=None):
    """Small helper to GET JSON from Adafruit IO REST API."""
    if not (AIO_USERNAME and AIO_KEY):
        raise RuntimeError("AIO_USERNAME or AIO_KEY is not set in .env")

    base = f"https://io.adafruit.com/api/v2/{AIO_USERNAME}"
    url = base + path
    headers = {"X-AIO-Key": AIO_KEY}
    r = requests.get(url, headers=headers, params=params, timeout=5)
    r.raise_for_status()
    return r.json()


def aio_get_last_points(feed_key: str, limit: int = 20):
    """Return (labels, values) for a feed using its key."""
    data = _aio_get_json(f"/feeds/{feed_key}/data", params={"limit": limit})
    data = list(reversed(data))
    labels = [item["created_at"][11:19] for item in data]
    values = []
    for item in data:
        try:
            values.append(float(item["value"]))
        except Exception:
            values.append(None)
    return labels, values


def aio_get_last_value(feed_key: str) -> str | None:
    """Return last value (string) of a feed, or None if error."""
    try:
        items = _aio_get_json(f"/feeds/{feed_key}/data", params={"limit": 1})
        if not items:
            return None
        return str(items[0]["value"])
    except Exception:
        return None


def send_aio_to_feed(feed_key: str, value: str):
    """Generic helper: publish a value to any Adafruit IO feed."""
    if not (AIO_USERNAME and AIO_KEY):
        raise RuntimeError("AIO_USERNAME or AIO_KEY is not set in .env")

    url = f"https://io.adafruit.com/api/v2/{AIO_USERNAME}/feeds/{feed_key}/data"
    headers = {
        "X-AIO-Key": AIO_KEY,
        "Content-Type": "application/json",
    }
    payload = {"value": value}
    r = requests.post(url, json=payload, headers=headers, timeout=5)
    r.raise_for_status()


# ------------ ROUTES USING TEMPLATES ------------

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/api/live")
def api_live():
    """Return live data from Adafruit IO for home dashboard."""
    try:
        labels_u, ultra_vals = aio_get_last_points(AIO_ULTRA_HTTP_FEED, limit=20)
        labels_g, gray_vals = aio_get_last_points(AIO_GRAY_MID_HTTP_FEED, limit=20)
        labels = labels_u or labels_g
        tts_text = aio_get_last_value(AIO_TTS_FEED) or "(no TTS data)"

        return jsonify(
            {
                "labels": labels,
                "ultrasonic": ultra_vals,
                "gray_mid": gray_vals,
                "tts": tts_text,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/about")
def about():
    return render_template("about.html")


# ------------ HISTORICAL DATA (Neon) ------------

@app.route("/sensor-data")
def sensor_data():
    """Table view of historical data for a chosen date (from Neon)."""
    date_str = request.args.get("date")
    try:
        chosen_date = date.fromisoformat(date_str) if date_str else date.today()
    except ValueError:
        chosen_date = date.today()

    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(
                """
                SELECT ts_utc, sensor_name, value
                FROM sensor_readings
                WHERE ts_utc::date = %s
                ORDER BY ts_utc DESC
                LIMIT 200;
                """,
                (chosen_date,),
            )
            rows = cur.fetchall()

    return render_template(
        "sensor_data.html",
        rows=rows,
        chosen_date=chosen_date.isoformat(),
    )


@app.route("/ultrasonic")
def ultrasonic_chart():
    """Line chart of ultrasonic_distance for a chosen date (from Neon)."""
    date_str = request.args.get("date")
    try:
        chosen_date = date.fromisoformat(date_str) if date_str else date.today()
    except ValueError:
        chosen_date = date.today()

    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(
                """
                SELECT ts_utc, value
                FROM sensor_readings
                WHERE sensor_name = 'ultrasonic_distance'
                  AND ts_utc::date = %s
                ORDER BY ts_utc ASC
                LIMIT 500;
                """,
                (chosen_date,),
            )
            rows = cur.fetchall()

    labels = [r["ts_utc"].strftime("%H:%M:%S") for r in rows]

    def to_float(v):
        try:
            return float(v)
        except Exception:
            return None

    values = [to_float(r["value"]) for r in rows]

    return render_template(
        "charts_ultra.html",
        labels=labels,
        values=values,
        chosen_date=chosen_date.isoformat(),
    )


@app.route("/grayscale")
def grayscale_chart():
    """Chart of grayscale_left/mid/right for a chosen date."""
    date_str = request.args.get("date")
    try:
        chosen_date = date.fromisoformat(date_str) if date_str else date.today()
    except ValueError:
        chosen_date = date.today()

    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(
                """
                SELECT ts_utc, sensor_name, value
                FROM sensor_readings
                WHERE sensor_name IN ('grayscale_left', 'grayscale_mid', 'grayscale_right')
                  AND ts_utc::date = %s
                ORDER BY ts_utc ASC;
                """,
                (chosen_date,),
            )
            rows = cur.fetchall()

    data_map = {}
    for r in rows:
        ts = r["ts_utc"].strftime("%H:%M:%S")
        name = r["sensor_name"]
        try:
            val = float(r["value"])
        except Exception:
            val = None
        data_map.setdefault(ts, {})[name] = val

    labels = sorted(data_map.keys())
    left_vals = [data_map[t].get("grayscale_left") for t in labels]
    mid_vals = [data_map[t].get("grayscale_mid") for t in labels]
    right_vals = [data_map[t].get("grayscale_right") for t in labels]

    return render_template(
        "charts_gray.html",
        labels=labels,
        left_vals=left_vals,
        mid_vals=mid_vals,
        right_vals=right_vals,
        chosen_date=chosen_date.isoformat(),
    )


# ------------ DEVICE 1: MOTORS ------------

@app.route("/control")
def control_motors():
    return render_template(
        "control_motors.html",
        command_feed=AIO_COMMAND_FEED,
    )


@app.route("/api/control", methods=["POST"])
def api_control():
    payload = request.get_json(silent=True) or {}
    direction = payload.get("direction")

    allowed = {"forward", "backward", "stop"}
    if direction not in allowed:
        return jsonify({"error": "invalid direction"}), 400

    try:
        send_aio_to_feed(AIO_COMMAND_FEED, direction)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------ DEVICE 2: STEERING (DIRECTION SERVO) ------------

@app.route("/steering")
def control_steering():
    return render_template(
        "steering.html",
        steering_feed=AIO_STEERING_FEED,
    )


@app.route("/api/steering", methods=["POST"])
def api_steering():
    payload = request.get_json(silent=True) or {}
    direction = payload.get("direction")

    allowed = {"left", "right", "center"}
    if direction not in allowed:
        return jsonify({"error": "invalid steering direction"}), 400

    try:
        send_aio_to_feed(AIO_STEERING_FEED, direction)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------ DEVICE 3: CAMERA SERVOS ------------

@app.route("/camera-control")
def camera_control():
    return render_template(
        "camera.html",
        camera_feed=AIO_CAMERA_FEED,
    )


@app.route("/api/camera", methods=["POST"])
def api_camera():
    payload = request.get_json(silent=True) or {}
    command = payload.get("command")

    allowed = {"pan_left", "pan_right", "pan_center", "tilt_up", "tilt_down", "tilt_center"}
    if command not in allowed:
        return jsonify({"error": "invalid camera command"}), 400

    try:
        send_aio_to_feed(AIO_CAMERA_FEED, command)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------ TTS (TEXT-TO-SPEECH) CONTROL ------------

@app.route("/tts-control", methods=["GET", "POST"])
def tts_control():
    msg_ok = None
    msg_err = None

    if request.method == "POST":
        text = request.form.get("text", "").strip()
        print("DEBUG /tts-control text from form:", repr(text))

        if not text:
            msg_err = "Please enter some text to speak."
        else:
            try:
                send_aio_to_feed(AIO_TTS_FEED, text)
                msg_ok = f"TTS command sent: '{text}'"
            except Exception as e:
                msg_err = f"Error sending TTS: {e}"

    return render_template(
        "tts_control.html",
        tts_feed=AIO_TTS_FEED,
        msg_ok=msg_ok,
        msg_err=msg_err,
    )


# ------------ LINE TRACKING ------------

@app.route("/line-tracking", methods=["GET", "POST"])
def line_tracking():
    msg_ok = None
    msg_err = None

    if request.method == "POST":
        cmd = request.form.get("cmd")
        if cmd not in {"start", "stop"}:
            msg_err = "Invalid command."
        else:
            try:
                send_aio_to_feed(AIO_LINE_FEED, cmd)
                msg_ok = f"Command '{cmd}' sent to feed '{AIO_LINE_FEED}'."
            except Exception as e:
                msg_err = f"Error sending command: {e}"

    return render_template(
        "line_tracking.html",
        line_feed=AIO_LINE_FEED,
        msg_ok=msg_ok,
        msg_err=msg_err,
    )


# ------------ OBSTACLE AVOIDANCE ------------

@app.route("/obstacle-avoidance", methods=["GET", "POST"])
def obstacle_avoidance():
    msg_ok = None
    msg_err = None

    if request.method == "POST":
        cmd = request.form.get("cmd")
        if cmd not in {"start", "stop"}:
            msg_err = "Invalid command."
        else:
            try:
                send_aio_to_feed(AIO_OBSTACLE_FEED, cmd)
                msg_ok = f"Command '{cmd}' sent to feed '{AIO_OBSTACLE_FEED}'."
            except Exception as e:
                msg_err = f"Error sending command: {e}"

    return render_template(
        "obstacle.html",
        obstacle_feed=AIO_OBSTACLE_FEED,
        msg_ok=msg_ok,
        msg_err=msg_err,
    )


if __name__ == "__main__":
    app.run(debug=True)
