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

# modules for graphing:
import matplotlib.pyplot as plt
import io
import random
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import numpy as np
import datetime as dt

# modules for processing data:
import statistics
import math # (just in case)
import numpy as np # (for percentile)

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

'''
# create table for users

db.execute("CREATE TABLE IF NOT EXISTS 'users' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
            'username' TEXT NOT NULL, 'hash' TEXT NOT NULL);")

# create table for foods/ingredients

db.execute("CREATE TABLE IF NOT EXISTS 'foods' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
            'user_id' NUMERIC NOT NULL, 'food_item' TEXT NOT NULL, 'date' DATE );")

# create table for feelings (on a scale of 1 through 10)

db.execute("CREATE TABLE IF NOT EXISTS 'feelings' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
            'user_id' NUMERIC NOT NULL, 'feeling' INTEGER NOT NULL, 'date' DATE );")
'''

# give all templates a variable 'username' which will contain current users username
# for now, using session["username"] instead
'''@app.context_processor
def inject_user():
    # if there is no username, assign "guest"
    if session.get("user_id") is None:
        username = "guest"
    else:
        # look up the users id in the database
        username = db.execute("SELECT username FROM users WHERE id=:id", id = session["user_id"])[0]["username"]
    return dict(username=username)
'''
# TODO: set the api_key to spoonacular key
# run export API_KEY=value in terminal

'''Commenting this out for now
# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")
'''

@app.route("/")
@login_required
def index():
    # track possible food sensitivity as follows:
    '''
    Let m be the mean feeling. Whenever a feeling dips below the mean feeling, record
    that as a time t_i. Set a time value for d, the digestion time and a sensitivity
    value epsilon. Let s_j(food) be the time you eat a certain food.
    Record whenever a time t_i is within epsilon of an s_j(food)+d (i.e. when
    the end of digestion is near a period of low feeling). Add up these numbers for
    each food to get a number n_d(food). Calculate n_d(food) for varying d, and
    take the maximum n_d(food). Record for each food.
    These are the foods that the program suspects.
    '''
    # TODO: make digestion time d and epsilon changeable by the user
    # estimated digestion time
    # currently minimum digestion time
    # currently setting via session["d"]
    d = session["d"]
    # d = dt.timedelta(hours=1)
    # how sensitive the filter is (more epsilon means more foods suspected)
    # currently setting via session["epsilon"]
    epsilon = session["epsilon"]
    # epsilon = dt.timedelta(hours=4)
    # calculate mean feeling
    if session["feeling_list"]:
        mean_feeling = statistics.mean([item["feeling"] for item in \
                        session["feeling_list"]])
    # if there are no recorded feelings, assume mean_feeling is 10
    else:
        mean_feeling = 10
    # put the times when feeling was below mean into a list of dicts
    # (same format as feeling_list)
    low_feeling_dict = \
        [item for item in session["feeling_list"] if \
                item["feeling"] < mean_feeling and item["feeling"] < 8]
    # define dict of n_d(food) numbers (format {"food":(int) n_d(food)})
    n_d = {food : 0 for food in session["food_list"]}
    for food in session["food_list"]:
        for t_food in session[food]:
            if any(t_food + d - epsilon < t["date"] < t_food + d + epsilon \
                    for t in low_feeling_dict):
                n_d[food] += 1
    suspected_foods = [(key,value) for key, value in n_d.items() \
                if np.percentile(list(n_d.values()), 90) < value]
    n("eggs", low_feeling_dict)
    return render_template("index.html", suspected_foods=suspected_foods)

def n(food, low_feeling_dict):
    # set d = min time of digestion (dt.timedelta type)
    d = session["d"]
    # n will be the max nd over all d coupled with avg feeling for that d
    # nd, d, avg feeling
    n = (0, d, 10)
    while d < dt.timedelta(days=1):
        if n[0] < nd(d,food, low_feeling_dict)[0]:
            n = nd(d, food, low_feeling_dict)
        d += dt.timedelta(hours=1)
    display_d = " ".join(str(d).split(":")[:-2]) + " hours"
    display_n = (n[0], display_d, n[2])
    return flash(display_n)

def nd(d,food, low_feeling_dict):
    # if food is not a session key, return 0
    try:
        session[food]
    except KeyError:
        return (0,d,10)
    nd = 0
    low_feelings = []
    epsilon = session["epsilon"]
    for t_food in session[food]:
        for t in low_feeling_dict:
            if t_food + d - epsilon < t["date"] < t_food + d + epsilon:
                nd += 1
                low_feelings.append(t["feeling"])
    if low_feelings:
        avg_feeling = round(statistics.mean(low_feelings))
    else:
        avg_feeling = 10
    return (nd, d, avg_feeling)

# TODO: make a way to remove foods/feelings from the database

@app.route('/plot.png')
def plot_png():
    '''route to plot graph of food vs feelings'''
    # make the graph
    fig = create_figure()
    # put graph in an io stream
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_figure():
    # create the figure
    # first, get user id
    user_id = session["user_id"]
    # create figure and subfigure
    fig = Figure(figsize=(10,7.5))
    # sub will put plots on top of fig
    sub = fig.subplots()
    # baseline minimum x dates are 12/20/20 at 8am
    xmin = dt.datetime.strptime("12/20/20 8am","%m/%d/%y %I%p")
    # baseline maximum x date is now
    xmax = dt.datetime.now()

    for food in session["food_list"]:
        # for each food, get the list of times that food was eaten by the current user
        # of the form datetimes in PDT
        x = session[food]
        # crude hash map to get different foods to not overlap in the graph
        yval = sum(map(ord,food)) % 10
        # for each food, print all the same y values
        y = [yval]*len(x)
        # update xmin and xmax if necessary. default settings are in case for
        # some reason x is empty
        #TODO: perform these min and max comparisons at login to save image load-time
        xmin = min(xmin, min(x, default=xmin))
        xmax = max(xmax, max(x, default=xmax))

        # TODO: make the "o"'s into pictures of that food

        # plot the food
        sub.plot(x,y,"o", label=food)

    # make a list of all the feeling data (in the form {"feeling":7, "date": (a date)})
    feelinglist = session["feeling_list"]
    # pick out dates from feeling list
    x = [item["date"] for item in feelinglist]
    # convert the dates to datetime.datetime object
    #x = [ dt.datetime.strptime(item["date"], '%Y-%m-%d %H:%M:%S') for item in feelinglist]
    # y-values for feeling is the feeling number given
    y = [ item["feeling"] for item in feelinglist]
    #TODO: perform these min and max comparisons at login to save image load-time
    # update xmin and xmax, add/subtract a margin of 8 hours to display end cases
    xmin = min(xmin, min(x, default=xmin)) - dt.timedelta(hours=8)
    xmax = max(xmax, max(x, default=xmax)) + dt.timedelta(hours=8)
    # plot the feelings
    sub.plot(x,y, "x", label="feeling")
    # set x limits to xmin and xmax
    sub.set_xlim([xmin, xmax])
    # set the axis labels
    sub.set_xlabel('Date')
    sub.set_ylabel('Food/Feeling')
    #create a legend
    sub.legend(fontsize=10,loc='best')

    '''The following format dates on the x axis in a fancy way,
    but they seem a little buggy'''
    #sub.xaxis.set_major_formatter(mdates.DateFormatter('%-I%p : %-m/%-d'))
    #sub.xaxis.set_major_locator(mdates.AutoDateLocator())
    #fig.autofmt_xdate()

    # return the figure
    return fig

@app.route("/eat", methods=["GET", "POST"])
@login_required
def eat():
    """Eat a food/ingredient"""

    #TODO: Incorporate spoonacular api to be able to search for ingredients

    if request.method == "POST":
        # read food eaten
        food = request.form.get("food")
        # get user id
        user_id = session["user_id"]
        # get date from the form (optional)
        date = request.form.get("date")
        if date:
            # if a date was given, parse the date into a datetime object (PDT)

            # TODO: make dates easier to enter

            date = dt.datetime.strptime(date,"%m/%d/%y %I %p")
        else:
            # if no date was given, choose the present as the date, convert to PDT
            date = datetime.now() - dt.timedelta(hours=7)
        # get the username
        username = session["username"]
        # update the foods table with the given information (food, date, user_id)
        db.execute("INSERT INTO foods (user_id, food_item, date) \
                    VALUES (:user_id, :food_item, :date)", user_id=user_id, food_item=food, date=date)
        # update the food_list session variable with the information (this will get overridden
        # with information from the database the next time the user logs in)
        if food in session["food_list"]:
            # this will be slightly different (decimal seconds) than the version loaded into session variable
            session[food].append(date)
            # another possible (complicated) way to do this (to avoid decimal seconds)
            #session[food].append(dt.datetime.strptime(dt.datetime.strftime(date, '%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S'))
        else:
            session["food_list"].append(food)
            # this will be slightly different (decimal seconds) than the version loaded into session variable
            session[food] = [date]
            #session[food] = [dt.datetime.strftime(date, '%Y-%m-%d %H:%M:%S')]
        # Thank the user for eating the food
        flash(f"Thanks for eating {food}, {username}!")
        # go back to the home page
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
        # read optional date
        date = request.form.get("date")
        if date:
            # if a date was given, read it and convert to datetime object in PDT
            date = dt.datetime.strptime(date,"%m/%d/%y %I %p")
        else:
            # if no date was given, assume the date is now
            date = datetime.now() - dt.timedelta(hours=7)
        # get username
        username = session["username"]
        # update the table feelings with the new data
        db.execute("INSERT INTO feelings (user_id, feeling, date) \
                    VALUES (:user_id, :feeling, \
                    :date)", user_id=session["user_id"], feeling=feeling, date=date)
        # update the session variable with the information.
        # this will get overridden next time the user logs in
        session["feeling_list"].append({"feeling":int(feeling), "date": date})
        # thank the user for recording a feeling
        flash(f"Thanks for recording how you are feeling, {username}. ")
        # encourage the user depending on how they are feeling
        if int(feeling) >= 7:
            flash("We are happy you are feeling good!")
        elif int(feeling) < 7 and int(feeling) > 3:
            flash("Hang in there!")
        else:
            flash("We hope you feel better soon!")
        # return to home page
        return redirect("/")
    else:
        # if the user is just visiting the page (not submitting form), display the page
        return render_template("record.html")

@app.route("/history")
@login_required
def history():
    """Show history"""
    #TODO (maybe) load this into a session variable
    foods = db.execute("SELECT date, food_item FROM foods WHERE user_id=:user_id", user_id=session["user_id"])

    return render_template("history.html", foods=foods)

@app.route("/graph")
@login_required
def graph():
    """Show graph"""
    return render_template("graph.html")

##############################################################################################################
'''login/logout stuff below'''
##############################################################################################################

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
        ################################################################################################
        '''session variable assignment below'''
        ###############################################################################################
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Remember username as string
        session["username"] = request.form.get("username")

        # Set users minimum digestion time

        session["d"] = dt.timedelta(hours=1)

        # set sensitivity

        session["epsilon"] = dt.timedelta(hours=4)

        # Remember foodlist (list of all distinct foods the user ate) (strings)
        session["food_list"] = [food["food_item"] for food in db.execute("SELECT DISTINCT \
                        food_item FROM foods WHERE user_id=:user_id", user_id = session["user_id"])]

        # Remember feeling list (list of dictionaries of how the user felt and when) [{feeling:_, date:_}]
        pre_feeling = db.execute("SELECT feeling, date FROM feelings \
                            WHERE user_id=:user_id ORDER BY date", user_id = session["user_id"])
        # convert the dates in feeling_list to datetime.datetime object
        # time zone should already be PDT
        session["feeling_list"] = [ {\
                    "feeling" : int(item["feeling"]), \
                    "date" : dt.datetime.strptime(item["date"], '%Y-%m-%d %H:%M:%S') \
                    } for item in pre_feeling]
        # Remember date when each food was eaten
        # in the form of a list of str(datetime) objects in GMT time

        # TODO (maybe): convert food list to have current (PDT) timezone

        for food in session["food_list"]:
            if food in ["user_id", "username", "food_list", "feeling_list"]:
                continue
            # list of str(datetime) objects
            pre_food = [time["date"] for time in db.execute("SELECT date FROM \
            foods WHERE user_id=:user_id AND \
            food_item=:food_item ORDER BY date", user_id = session["user_id"], food_item = food)]
            # convert the list (list elements are of type str(datetime.datetime)) to datetime.datetime objects
            # timezone should be in PDT
            session[food] = [dt.datetime.strptime(time, '%Y-%m-%d %H:%M:%S') \
                        for time in pre_food]

        #########################################################################################################
        '''end storing session variables'''
        ###########################################################################################################

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
