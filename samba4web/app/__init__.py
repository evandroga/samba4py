from flask import Flask
from .views.users import users
from .views.groups import groups
from .views.gpo import gpo

app = Flask(__name__)
app.register_blueprint(users)
app.register_blueprint(groups)
app.register_blueprint(gpo)
