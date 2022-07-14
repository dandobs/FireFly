from flask import Flask

app = Flask(__name__)

# Following syntax structured this way to avoid circular imports
from app import views