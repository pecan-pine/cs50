import os
import sys

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, send_from_directory
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup

# for graphing:
import matplotlib.pyplot as plt
import io
import random
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import datetime as dt


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///food.db")

# create table for users

db.execute("CREATE TABLE IF NOT EXISTS 'users' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
            'username' TEXT NOT NULL, 'hash' TEXT NOT NULL);")

# create table for foods/ingredients

db.execute("CREATE TABLE IF NOT EXISTS 'foods' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
            'user_id' NUMERIC NOT NULL, 'food_item' TEXT NOT NULL, 'date' DATE );")

# create table for feelings (on a scale of 1 through 10)

db.execute("CREATE TABLE IF NOT EXISTS 'feelings' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
            'user_id' NUMERIC NOT NULL, 'feeling' INTEGER NOT NULL, 'date' DATE );")

# give all templates a variable 'username' which will contain current users username
@app.context_processor
def inject_user():
    # if there is no username, assign "guest"
    if session.get("user_id") is None:
        username = "guest"
    else:
        # look up the users id in the database
        username = db.execute("SELECT username FROM users WHERE id=:id", id = session["user_id"])[0]["username"]
    return dict(username=username)

# TODO: set the api_key to spoonacular key
# run export API_KEY=value in terminal

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

@app.route('/plot.png')
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_figure():
    """    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = range(100)
    ys = [random.randint(1, 50) for x in xs]
    axis.plot(xs, ys)
    return fig
"""
#create figure and subfigure
    # fig = plt.figure(figsize=(10,10))
    fig = Figure(figsize=(10,7.5))
    sub = fig.subplots()
    sub.set_xlabel('Year')
    sub.set_ylabel('Numbe of People')
    x_val = [1,2,3,4]
    y_val = [1,2,1,2]
    name = "emma"
    gender = "F"
    sub.plot(x_val,y_val, label="Name="+name.capitalize()+", Gender="+gender)
    #create a legend
    sub.legend(fontsize=10,loc='best')
    return fig

@app.route('/plot2.png')
def plot2_png():
    fig = create_figure2()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    print_this()
    return Response(output.getvalue(), mimetype='image/png')

def print_this():
    feelinglist = db.execute("SELECT feeling, date FROM feelings WHERE user_id=:user_id ORDER BY date", user_id = 2)
    x = [item["date"] for item in feelinglist]
    y = [ int(item["feeling"]) for item in feelinglist]
    return print([feelinglist, x, y], file=sys.stdout)

def create_figure2():
    #create figure and subfigure
    fig = Figure(figsize=(10,7.5))
    sub = fig.subplots()
    foodlist = [food["food_item"] for food in db.execute("SELECT DISTINCT food_item FROM foods WHERE user_id=:user_id", user_id = 2)]
    for food in foodlist:
        x = [time["date"] for time in db.execute("SELECT date FROM \
                    foods WHERE user_id=:user_id AND food_item=:food_item ORDER BY date", user_id = 2, food_item = food)]
        x = [dt.datetime.strptime(time, '%Y-%m-%d %H:%M:%S') - dt.timedelta(hours=7) for time in x]
        x.append(dt.datetime.now())
        y = range(0,len(x))
        # TODO: make the "o"'s into pictures of that food
        sub.plot(x,y,"o", label=food)
    d = dt.datetime.now()
    l = []
    for i in range(-4,0):
        l.append(d - dt.timedelta(hours=3*i))
    y = [1]*len(l)
    sub.plot(l,y)

    feelinglist = db.execute("SELECT feeling, date FROM feelings WHERE user_id=:user_id ORDER BY date", user_id = 2)
    x = [ dt.datetime.strptime(item["date"], '%Y-%m-%d %H:%M:%S') - dt.timedelta(hours=7) for item in feelinglist]
    y = [ int(item["feeling"]) for item in feelinglist]
    sub.plot(x,y, "o", label="feeling")

    sub.xaxis.set_major_formatter(mdates.DateFormatter('%-I%p : %-m/%-d'))
    sub.xaxis.set_major_locator(mdates.AutoDateLocator())
    #create a legend
    sub.legend(fontsize=10,loc='best')
    fig.autofmt_xdate()
    return fig


@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/eat", methods=["GET", "POST"])
@login_required
def eat():
    """Eat a food/ingredient"""

    #TODO: Incorporate spoonacular api to be able to search for ingredients

    if request.method == "POST":
        # read food eaten
        food = request.form.get("food")
        user_id = session["user_id"]
        username = db.execute("SELECT username FROM users WHERE id = :user_id", user_id = user_id)[0]["username"]
        date = datetime.now()
        db.execute("INSERT INTO foods (user_id, food_item, date) \
                    VALUES (:user_id, :food_item, :date)", user_id=user_id, food_item=food, date=date)
        flash(f"Thanks for eating {food}, {username}!")
        return redirect("/")
    else:
        # if the user is just visiting the page (not submitting form), display the page
        return render_template("eat.html")

@app.route("/record", methods=["GET", "POST"])
@login_required
def record():
    """Record a feeling"""

    #TODO: Incorporate spoonacular api to be able to search for ingredients

    if request.method == "POST":
        # read feeling recorded
        feeling = request.form.get("feeling")
        user_id = session["user_id"]
        username = db.execute("SELECT username FROM users WHERE id = :user_id", user_id = user_id)[0]["username"]
        date = datetime.now()
        db.execute("INSERT INTO feelings (user_id, feeling, date) \
                    VALUES (:user_id, :feeling, :date)", user_id=user_id, feeling=feeling, date=date)
        flash(f"Thanks for recording how you are feeling, {username}. ")
        if int(feeling) >= 7:
            flash("We are happy you are feeling good!")
        elif int(feeling) < 7 and int(feeling) > 3:
            flash("Hang in there!")
        else:
            flash("We hope you feel better soon!")
        return redirect("/")
    else:
        # if the user is just visiting the page (not submitting form), display the page
        return render_template("record.html")

@app.route("/history")
@login_required
def history():
    """Show history"""
    foods = db.execute("SELECT date, food_item FROM foods WHERE user_id=:user_id", user_id=session["user_id"])

    return render_template("history.html", foods=foods)

@app.route("/graph")
@login_required
def graph():
    """Show graph"""
    # TODO
    foods = db.execute("SELECT date, food_item FROM foods WHERE user_id=:user_id", user_id=session["user_id"])

    return render_template("graph.html", foods=foods)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", message="must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", message="must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html", message="invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("register.html", message="must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("register.html", message="must provide password")

        # ensure password confirmation was given
        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("register.html", message="passwords do not match")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
        # Ensure username is not already in database
        if len(rows) != 0:
            return render_template("register.html", message="Username taken")

        # put user information into the database
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=request.form.get("username"), hash=generate_password_hash(request.form.get("password")))

        # TODO: make the user automatically get logged in after registering?

        # Remember which user has logged in
        # session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")



def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
