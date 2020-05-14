import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd

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

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# create table for purchases

db.execute("CREATE TABLE IF NOT EXISTS 'purchases' ('purchase_id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
            'user_id' NUMERIC NOT NULL, 'stock_symbol' TEXT NOT NULL, 'purchase_date' DATE, \
            'share_value' NUMERIC, 'num_shares' NUMERIC);")

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

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    # get users current amount of cash as a number
    cash = db.execute("SELECT cash FROM users WHERE id=:user_id", user_id=user_id)[0]["cash"]
    # total value so far (not counting stock value yet)
    total = round(cash, 2)
    # convert cash to usd string to display
    cash_display = usd(cash)
    # get total stocks owned by user, grouped by stock
    stocks = db.execute("SELECT stock_symbol, sum(num_shares) as shares \
                    FROM purchases WHERE user_id=:user_id GROUP BY stock_symbol", user_id=user_id)
    # Symbol Name Amount Owned Current Price Total Value
    # list to display stock data
    display_list = []
    for stock in stocks:
        # store information for each stock in a dict
        stock_dict = {}
        # check if there are 0 shares of the stock:
        # if there are, continue in loop, skipping this stock
        if stock["shares"] == 0:
            continue
        # place number of shares into dictionary
        stock_dict["amount"] = stock["shares"]
        # create variable symbol for the stock symbol
        symbol = stock["stock_symbol"]
        # place stock symbol into dictionary
        stock_dict["symbol"] = symbol
        # place stock name into dictionary
        stock_dict["name"] = lookup(symbol)["name"]
        # lookup current price and place in dictionary
        stock_dict["price"] = lookup(symbol)["price"]
        # calculate value as price * number of stocks
        value = stock_dict["price"] * stock_dict["amount"]
        # store a display version of the value in the dict
        stock_dict["value"] = usd( value )
        # add the rounded value to the total money
        total += round(value, 2)
        # add this stocks dict to the list
        display_list.append(stock_dict)

    # make the page
    return render_template("index.html", cash=cash_display, stocks=display_list, \
                            total=usd(total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        # read number of shares requested (as text)
        shares = request.form.get("shares")
        # if the given symbol cannot be found on IEX, return apology
        if not lookup(request.form.get("symbol")):
            return apology("Could not find symbol", 403)
        # if the number of shares is not a positive integer
        elif (not shares.isdigit() or int(shares) <= 0):
            return apology("Please enter a positive integer for shares.", 403)
        # convert number of shares to number
        shares = int(shares)
        # find price, symbol, user id, current time
        price = lookup(request.form.get("symbol"))["price"]
        symbol = lookup(request.form.get("symbol"))["symbol"]
        user_id = session["user_id"]
        date = datetime.now()
        # find users available cash
        cash = db.execute("SELECT cash FROM users WHERE id=:user_id",user_id=user_id)[0]["cash"]
        # users hypothetical balance after purchase
        balance = cash - shares * price
        # TABLE 'purchases' |'user_id'|'stock_symbol'|'purchase_date'|'share_value'|'num_shares'|
        # dont buy stocks if there is not enough money
        if balance < 0:
            return apology("you don't have enough money to buy these stocks", 403)
        # if there is enough money, make a database table entry for the purchase
        db.execute("INSERT INTO purchases \
            (user_id, stock_symbol, purchase_date, share_value, num_shares) \
            VALUES (:user_id, :symbol, :date, :price, :shares)", \
            user_id=user_id, symbol=symbol, date=date, price=price, shares=shares)
        # update users cash balance
        db.execute("UPDATE users SET cash=:balance WHERE id=:user_id", user_id=user_id, balance=balance)
        # redirect to home page

        # TODO: redirect while alerting the user that a purchase has occured
        return redirect("/")
    else:
        # if the user is just visiting the page (not submitting form), display the page
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    # find the user-input symbol. This should be an empty string until the
    # user enters something in
    symbol = request.form.get("symbol")
    # error message in case an invalid symbol gets entered
    quoteError = "Could not find that symbol. Please enter another."
    if request.method=="POST":
        # if the symbol is not in IEX database, return an error message
        if not lookup(symbol):
            return render_template("quote.html", quoteError=quoteError)
        # find name price and symbol of the stock symbol
        name = lookup(symbol)['name']
        price = lookup(symbol)['price']
        symbol = lookup(symbol)['symbol']
        # display the page with the given information
        return render_template("quoted.html", name=name, price=price, symbol=symbol)
    else:
        # if the user is GET-ing the webpage, display it
        return render_template("quote.html", quoteError="")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # ensure password confirmation was given
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
        # Ensure username is not already in database
        if len(rows) != 0:
            return apology("Username taken", 403)

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


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # set user_id as current user's id
    user_id = session["user_id"]
    # get total stocks owned by user, grouped by stock
    stocks = db.execute("SELECT stock_symbol, SUM(num_shares) as shares \
                    FROM purchases WHERE user_id=:user_id GROUP BY stock_symbol", user_id=user_id)

    # pick out only those stocks where the user owns at least 1
    # (assuming number of stocks is >= 0 here)
    stocks = [stock for stock in stocks if not stock["shares"] == 0]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # user's desired stock to sell
        symbol = request.form.get("symbol")
        # if symbol was left blank (not selected), return an apology
        if not symbol:
            return apology("please select a stock to sell", 403)
        # if the selected stock is not in the users list of stocks, return an apology
        elif (not any([symbol in stock.values() for stock in stocks])):
            return apology("you do not own any shares of this stock")
        # shorten the list of stocks to only the selected one
        # (this assumes that at this point only one element of the list matches with symbol)
        # also, pick this_stock's dictionary out of the list
        this_stock = [stock for stock in stocks if stock["stock_symbol"] == symbol][0]
        # get number of shares owned of this stock
        shares_owned = this_stock["shares"]
        # another way to get shares owned: query the database
        # shares_owned = int( db.execute("SELECT sum(num_shares) as shares FROM purchases WHERE user_id=:user_id \
        #            and stock_symbol=:symbol", user_id=user_id, symbol=symbol)[0]["shares"] )
        # number of shares requested to sell in the form
        shares_requested = request.form.get("shares")
        # if the number of shares requested is not a positive integer, return an apology
        if (not shares_requested.isdigit() or int(shares_requested) <= 0):
            return apology("please enter a positive integer to sell")
        # convert shares requested to integer
        shares_requested = int(shares_requested)
        # if the user does not have this many shares, return an apology
        if shares_requested > shares_owned:
            return apology("you do not own that many shares of this stock")
        # today's date
        date = datetime.now()
        price = lookup(symbol)["price"]
        # if there is enough money, make a database table entry for the purchase
        db.execute("INSERT INTO purchases \
            (user_id, stock_symbol, purchase_date, share_value, num_shares) \
            VALUES (:user_id, :symbol, :date, :price, :shares)", \
            user_id=user_id, symbol=symbol, date=date, price=price, shares= -shares_requested)
        cash = db.execute("SELECT cash FROM users WHERE id=:user_id", user_id=user_id)[0]["cash"]
        value = round(price * shares_requested, 2)
        balance = value + cash
        # update users cash balance
        db.execute("UPDATE users SET cash=:balance WHERE id=:user_id", user_id=user_id, balance=balance)
        return redirect("/")
    else:
        return render_template("sell.html", stocks=stocks)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
