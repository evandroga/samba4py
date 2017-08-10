from flask import Blueprint, render_template

gpo = Blueprint('gpo', __name__)

@gpo.route('/')
def showGroups():
    render_template('gpo.html')

@gpo.route('/add')
def addGroups():
    pass
