from flask import render_template
from plotserver import app
from os import path

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def send_foo(filename):
    return app.send_static_file(path)
    
@app.route('/log.dat')
def send_odlog():
    with open('log.dat') as f:
        return f.read()