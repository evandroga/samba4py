from flask import Blueprint, render_template

users = Blueprint('users', __name__)

@users.route('/')
def showGroups():
    render_template('users.html')

@users.route('/add')
def addGroups():
    pass
