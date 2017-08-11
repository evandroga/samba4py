from flask import Blueprint, render_template

gpo = Blueprint('gpo', __name__)

@gpo.route('/')
def showGPO():
    render_template('gpo.html')

@gpo.route('/add')
def addGPO():
    pass
