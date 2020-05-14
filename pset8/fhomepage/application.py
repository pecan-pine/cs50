
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/age")
def age():
    return render_template("age.html")

@app.route("/diet")
def diet():
    return render_template("diet.html")

@app.route("/hobbies")
def hobbies():
    return render_template("hobbies.html")

@app.route("/pictures")
def pictures():
    return render_template("pictures.html")