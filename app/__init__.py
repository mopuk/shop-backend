from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, static_folder="../static")
db_uri = os.environ.get("DATABASE_URI")
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import models