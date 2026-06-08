"""
backend/app.py — Flask application factory.

Run with:  python -m backend.app
"""

from flask import Flask

def create_app():
    app = Flask(__name__)
    # TODO: import and register routes blueprint
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
