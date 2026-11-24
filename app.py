import os
import platform
import socket
import time
from datetime import datetime, timezone

import psutil
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
START_TIME = time.time()


class MetricSnapshot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recorded_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    cpu_percent = db.Column(db.Float, nullable=False)
    memory_percent = db.Column(db.Float, nullable=False)
    disk_percent = db.Column(db.Float, nullable=False)


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///cloudwatchtower.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.get("/")
    def dashboard():
        return render_template("dashboard.html", hostname=socket.gethostname())

    @app.get("/health")
    def health():
        return jsonify({
            "status": "ok",
            "application": "CloudWatchtower",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 200

    @app.get("/api/metrics")
    def metrics():
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        # Prime CPU measurement; the browser's next refresh receives a meaningful value.
        cpu = psutil.cpu_percent(interval=0.2)
        uptime_seconds = int(time.time() - psutil.boot_time())

        snapshot = MetricSnapshot(
            cpu_percent=cpu,
            memory_percent=memory.percent,
            disk_percent=disk.percent
        )
        db.session.add(snapshot)
        db.session.commit()

        return jsonify({
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "cpu_percent": cpu,
            "memory_percent": memory.percent,
            "memory_used_gb": round(memory.used / (1024 ** 3), 2),
            "memory_total_gb": round(memory.total / (1024 ** 3), 2),
            "disk_percent": disk.percent,
            "disk_used_gb": round(disk.used / (1024 ** 3), 2),
            "disk_total_gb": round(disk.total / (1024 ** 3), 2),
            "uptime_seconds": uptime_seconds,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    @app.get("/api/history")
    def history():
        rows = MetricSnapshot.query.order_by(MetricSnapshot.id.desc()).limit(20).all()
        return jsonify([
            {
                "timestamp": row.recorded_at.isoformat(),
                "cpu_percent": row.cpu_percent,
                "memory_percent": row.memory_percent,
                "disk_percent": row.disk_percent
            }
            for row in reversed(rows)
        ])

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=False)