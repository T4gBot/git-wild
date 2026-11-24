import os
import socket
from datetime import UTC, datetime

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.wrappers.response import Response

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

THEMES: dict[str, dict[str, str]] = {
    "default": {
        "title": "NERDS uc - Wild Cam Observation",
        "image": "🌿",
        "icon": "🌿",
    },
    "land": {
        "title": "NERDS uc - Land & Air Observation",
        "image": "🦌",
        "icon": "🦅",
    },
    "sea": {
        "title": "NERDS uc - Sea Observation",
        "image": "🐋",
        "icon": "🌊",
    },
}

APP_MODE = os.environ.get("APP_MODE", "default").strip().lower()
if APP_MODE not in THEMES:
    APP_MODE = "default"
THEME = THEMES[APP_MODE]


class Observation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal = db.Column(db.String(100), nullable=False)
    stream = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(UTC))


# Serialise create_all() across workers via a lock to avoid races that abort gunicorn
with app.app_context(), db.engine.begin() as conn:
    if conn.dialect.name == "postgresql":
        conn.execute(text("SELECT pg_advisory_xact_lock(727274)"))
    db.metadata.create_all(conn)


@app.context_processor
def inject_hostname() -> dict[str, str]:
    return {"hostname": socket.gethostname()}


@app.route("/whoami")
def whoami() -> str:
    return socket.gethostname()


@app.route("/", methods=["GET", "POST"])
def index() -> str | Response:
    if request.method == "POST":
        animal = request.form.get("animal")
        stream = request.form.get("stream")
        if animal and stream:
            new_obs = Observation(animal=animal, stream=stream, category=APP_MODE)
            db.session.add(new_obs)
            db.session.commit()
        return redirect(url_for("index"))

    observations = Observation.query.filter_by(category=APP_MODE).order_by(Observation.timestamp.desc()).all()
    return render_template(
        "index.html", observations=observations, app_mode=APP_MODE, theme=THEME
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8081"))
    app.run(host="0.0.0.0", port=port, debug=True)
