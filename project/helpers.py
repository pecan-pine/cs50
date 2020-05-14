import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    return render_template("apology.html", option=message, num=code)


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def picture(food):
    """Look up picture of ingredient."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        #response = requests.get(f"https://api.spoonacular.com/recipes/716429/information?apiKey={api_key}&includeNutrition=true")
        #response = requests.get(f"https://cloud-sse.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}")
        #https://spoonacular.com/cdn/ingredients_100x100/apple.jpg
        response = requests.get(f"https://api.spoonacular.com/food/ingredients/autocomplete?apiKey={api_key}&query={food}&number=1")
        response.raise_for_status()
    except requests.RequestException:
        print("error contacting spoonacular")
        return None

    # Parse response
    try:
        quote = response.json()
        if not quote:
            return quote
        image = quote[0]['image']
        return f"https://spoonacular.com/cdn/ingredients_100x100/{image}"

    except (KeyError, TypeError, ValueError):
        print("error parsing response from spoonacular")
        return None

def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        response = requests.get(f"https://cloud-sse.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None
