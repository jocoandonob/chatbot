import uvicorn
from fastapi.applications import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

from app import app as fastapi_app

# Create a simple Flask app for WSGI compatibility
from flask import Flask

flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return "This is a Flask app, but you should be accessing the FastAPI app."

# Add the Flask app as a WSGI application under a specific path
fastapi_app.mount("/flask", WSGIMiddleware(flask_app))

# This is the app that Gunicorn will use
app = fastapi_app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)