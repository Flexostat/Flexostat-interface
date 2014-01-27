from flask import render_template
from plotserver import app

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def send_foo(filename):
    return app.send_static_file(path)