from flask import render_template

from app import app

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/cases')
def cases():
    return render_template("cases.html")
