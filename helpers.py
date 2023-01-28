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


API_KEY = 1


"""lookup cocktails by name search"""
def cocktail_lu(cocktail_name):
    try:        
        url = f"https://www.thecocktaildb.com/api/json/v1/{API_KEY}/search.php"
        querystring = {"s": cocktail_name}

        response = requests.request("GET", url, params=querystring)
    
    except requests.RequestException:
        return None

    return response.json()["drinks"]


"""lookup single cocktail by idDrink"""
def recipe_lu(idDrink):
    try:
        url = f"https://www.thecocktaildb.com/api/json/v1/{API_KEY}/lookup.php"
        querystring = {"i": idDrink}

        response = requests.request("GET", url, params=querystring)

    except requests.RequestException:
        return None

    return response.json()["drinks"][0]


"""lookup ingredient by name search"""
def ingredient_lu(ingredient_name):
    try:
        url = f"https://www.thecocktaildb.com/api/json/v1/{API_KEY}/search.php"
        querystring = {"i": ingredient_name}

        response = requests.request("GET", url, params=querystring)
    
    except requests.RequestException:
        return None
    
    return response.json()["ingredients"]


"""lookup ingredient by id search - FUNCTION NOT USED"""
def ingredientId_lu(ingredient_id):
    try:
        url = f"https://www.thecocktaildb.com/api/json/v1/{API_KEY}/search.php"
        querystring = {"iid": ingredient_id}

        response = requests.request("GET", url, params=querystring)
    
    except requests.RequestException:
        return None
    
    return response.json()["ingredients"]


"""filter cocktails by multi-ingredients"""
def filter_multiingredients(my_ingredients):
    try: 
        url = "https://the-cocktail-db.p.rapidapi.com/filter.php"
        #querystring = {"i": ["anis,dry vermouth,gin", "lime,light rum,powdered sugar"]}
        querystring = {"i": ','.join(my_ingredients)}
        headers = {
            "X-RapidAPI-Key": "e5fb1c3756mshb2c2caf3ff051bep17550djsndcf1006181e8",
            "X-RapidAPI-Host": "the-cocktail-db.p.rapidapi.com"
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
    
    except requests.RequestException:
        return None

    return response.json()["drinks"]
