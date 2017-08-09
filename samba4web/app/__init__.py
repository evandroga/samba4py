from flask import Flask
from .views.users import users

app = Flask(__name__)
app.register_blueprint(users)
