from flask import redirect, render_template, request, session
from functools import wraps

import requests #required for API requests

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


"""lookup cocktails by name search"""
def cocktail_lu(cocktail_name):
    try:
        url = "https://the-cocktail-db.p.rapidapi.com/search.php"
        querystring = {"s": cocktail_name}
        headers = {
            "X-RapidAPI-Key": "e5fb1c3756mshb2c2caf3ff051bep17550djsndcf1006181e8",
            "X-RapidAPI-Host": "the-cocktail-db.p.rapidapi.com"
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
    
    except requests.RequestException:
        return None
    
    return response.json()["drinks"]

"""lookup single cocktail by idDrink"""
def recipe_lu(idDrink):
    try:
        url = "https://the-cocktail-db.p.rapidapi.com/lookup.php"
        querystring = {"i": idDrink}
        headers = {
        "X-RapidAPI-Key": "e5fb1c3756mshb2c2caf3ff051bep17550djsndcf1006181e8",
        "X-RapidAPI-Host": "the-cocktail-db.p.rapidapi.com"
        }
        response = requests.request("GET", url, headers=headers, params=querystring)

    except requests.RequestException:
        return None

    return response.json()["drinks"][0]