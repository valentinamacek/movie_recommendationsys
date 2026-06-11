"""
backend/app.py — Flask application factory.

Run with:  python -m backend.app
"""

from flask import Flask
from backend.routes import bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)