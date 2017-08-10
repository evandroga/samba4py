from flask import Blueprint, render_template

groups = Blueprint('groups', __name__)

@groups.route('/')
def showGroups():
    render_template('groups.html')

@groups.route('/add')
def addGroups():
    pass
