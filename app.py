from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from itertools import combinations #consider moving later to helpers.py
import json

from helpers import login_required, cocktail_lu, recipe_lu, ingredient_lu, filter_multiingredients


app = Flask(__name__)

db = SQL("sqlite:///cocktail.db")

"""keeps cache clear - delete aftewards"""
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


"""Configure session to use filesystem (instead of signed cookies)"""
"""CHANGE THIS IN PRE-PRODUCTION: https://medium.com/thedevproject/flask-sessions-what-are-they-for-how-it-works-what-options-i-have-to-persist-this-data-4ca48a34d3"""
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

"""global varuables"""
cocktails = {} #to be used in cocktail_lookup and basis for cocktail recipe

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")


        if not username:
            flash("Username field cannot be blank")
            return render_template("register.html"), 403
        if not password or not confirmation:
            flash("Password fields cannot be blank")
            return render_template("register.html"), 403
        elif password != confirmation:
            flash("Passwords do not match")
            return render_template("register.html"), 403


        rows = db.execute("SELECT * FROM users")
        for row in rows:
            if username == row["username"]:
                flash("Username already taken")
                return render_template("register.html"), 403

        """Writes new user into user database"""
        hashed_password = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES(?,?)", username, hashed_password)
        
        """Keeps new registered user logged in"""
        rows = db.execute("SELECT * FROM users where username = ?", username)
        session["user_id"] = rows[0]["id"]

        flash("Registered!")
        return redirect("/")

    return render_template("/register.html")
    

@app.route("/login", methods=["GET", "POST"])
def login():
    
    session.clear()

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            flash("Username field cannot be blank")
            return render_template("login.html"), 403

        elif not password:
            flash("Password field cannot be blank")
            return render_template("login.html"), 403

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("Invalid username and/or password")
            return render_template("login.html"), 403
        
        session["user_id"] = rows[0]["id"]
        
        flash("Logged in!")
        return redirect("/")

    return render_template("/login.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()

    flash("Logged out!")

    return redirect("/")


@app.route("/cocktail_lookup", methods=["GET", "POST"])
@login_required
def cocktail_lookup():
    
    if request.method == "POST":
        cocktails = cocktail_lu(request.form.get("cocktail"))

        #flash(cocktails[0]["strIngredient"+str(1)])
        return render_template("cocktail_lookup_result.html", cocktails=cocktails)

    return render_template("cocktail_lookup.html")

@app.route("/cocktail_recipe")
@login_required
def cocktail_recipe():

    #if request.args.get("create"):
    #    return redirect("/cocktail_lists")


    cocktail = recipe_lu(request.args.get("idDrink"))

    my_ingredients = db.execute("SELECT * FROM ingredients WHERE user_id = ?", session["user_id"])
    
    my_ingredients_list = []
    my_ingredient_name_list = []
    my_ingredient_type_list = []
    my_ingredients_by_type = {}
    for ingredient in my_ingredients:
        my_ingredients_list.append({"name": ingredient["name"], "type": ingredient["type"]})
        my_ingredient_name_list.append(ingredient["name"])
        my_ingredient_type_list.append(ingredient["type"])

        """populating dict variable: my_ingredients_by_type"""
        if ingredient["type"] == "None": #passes over all ingredients whose type is "None"
            pass
        elif ingredient["type"] not in my_ingredients_by_type.keys(): # adds key:value pair for first appearance of a key - the value is added as a list, thereby allowing to add several values
            my_ingredients_by_type.update({ingredient["type"]: [ingredient["name"]]})
        else: # adds ingredient value to key as additional list item
            my_ingredients_by_type[ingredient["type"]] += [ingredient["name"]]

    cocktail_ingredients_list = []
    for i in range(1, 15):
        if cocktail["strIngredient"+str(i)]:
            cocktail_ingredients_list.append({"name": cocktail["strIngredient"+str(i)], "type": ingredient_lu(cocktail["strIngredient"+str(i)])[0]["strType"]}) 
    
    """split into for loop in order to reduce api calls"""
    cocktail_ingredients_name_list = []
    cocktail_ingredients_type_list = []
    for ingredient in cocktail_ingredients_list:
        cocktail_ingredients_name_list.append(ingredient["name"])
        cocktail_ingredients_type_list.append(ingredient["type"])
    
    cocktail_nam_typ_dict = {}
    for ingredient in cocktail_ingredients_list:
        cocktail_nam_typ_dict.update({ingredient["name"]: ingredient["type"]})

    alt_type = []
    for ingredient in my_ingredient_name_list:
        if ingredient in cocktail_ingredients_name_list:
            pass
       #elif ingredient not in cocktail_ingredients_name_list:
    for ingr in cocktail_ingredients_name_list:
        if ingr in cocktail_nam_typ_dict.keys():
            alt_type.append(cocktail_nam_typ_dict[ingr])

    alt_ing_by_type = {}
    for cocktail_ingr_type in cocktail_ingredients_type_list:
        if cocktail_ingr_type in my_ingredients_by_type.keys():
            alt_ing_by_type[cocktail_ingr_type] = my_ingredients_by_type[cocktail_ingr_type]

    #04.02.2023 - CLEAN UP THIS SECTION!!


    my_cocktail_lists = db.execute("SELECT * FROM list_names WHERE user_id = ? AND category = 'cocktail'", session["user_id"])

    #flash(alt_ing_by_type)
    return render_template("cocktail_recipe.html", 
        cocktail=cocktail, 
        my_ingredient_name_list=my_ingredient_name_list, 
        alt_ing_by_type=alt_ing_by_type, 
        cocktail_nam_typ_dict=cocktail_nam_typ_dict, 
        my_cocktail_lists=my_cocktail_lists)


@app.route("/ingredient_lookup", methods=["GET", "POST"])
@login_required
def ingredient_lookup():
    
    if request.method == "POST":
        ingredients = ingredient_lu(request.form.get("ingredient"))

        return render_template("ingredient_lookup_result.html", ingredients=ingredients)

    return render_template("ingredient_lookup.html")


@app.route("/add_ingredient")
@login_required
def add_ingredient():

    api_id = request.args.get("idDrink")
    ingredient_name = request.args.get("name")
    ingredient_type = request.args.get("type")
    alcohol = request.args.get("alcohol")
    abv = request.args.get("abv")

    #check if ingredient already in database
    if db.execute("SELECT api_id FROM ingredients WHERE user_id = ? AND api_id = ?", session["user_id"], api_id):

        flash("Ingredient is already in your ingredient list!")
        return redirect("/ingredient_lookup")

    db.execute("INSERT INTO ingredients (user_id, api_id, name, type, alcohol, abv) VALUES(?,?,?,?, ?, ?)", session["user_id"], api_id, ingredient_name, ingredient_type, alcohol, abv)

    flash(ingredient_name + " added to your ingredient list!")
    return redirect("/ingredient_lookup")


@app.route("/ingredient_list")
@login_required
def ingredient_list():
    
    ingredients = db.execute("SELECT * FROM ingredients WHERE user_id = ?", session["user_id"])

    return render_template("ingredient_list.html", ingredients=ingredients)


@app.route("/remove_ingredient")
@login_required
def remove_ingredient():

    ingredient_id = request.args.get("id")
    ingredient_name = request.args.get("name")

    db.execute("DELETE FROM ingredients WHERE user_id = ? AND id = ?", session["user_id"], ingredient_id)

    flash(ingredient_name + " removed from your ingredient list!")
    return redirect("/ingredient_list")


@app.route("/my_bar")
@login_required
def my_bar():

    # pulls user's ingredients as dict
    my_ingredients = db.execute("SELECT name FROM ingredients WHERE user_id = ?", session["user_id"])
    
    # stores ingredients in list, instead of dict
    my_ingredients_list = []
    for ingredient in my_ingredients:
        my_ingredients_list.append(ingredient["name"])

    my_cocktails = []
    #my_cocktails = filter_multiingredients(my_ingredients_list)

    # generate all possible ingredient combination, with minimum 2 ingredients
    ingr_combinations = []
    for length in range(2, len(my_ingredients_list)+1):
        for subset in combinations(my_ingredients_list, length):
            ingr_combinations.append(subset)

    # create (non-distinct) list of cocktails based on all possible ingredient combinations
    for row in ingr_combinations:
        my_cocktails.extend(filter_multiingredients(row))

    # remove duplicate cocktails from my_cocktails / get distinct list of cocktails from my_cocktails
    my_cocktails = list(
        {
            drink["idDrink"]: drink
            for drink in my_cocktails
        }.values()
    )

    #flash(my_ingredients_list)
    return render_template("my_bar.html", cocktails=my_cocktails)


@app.route("/cocktail_lists")
@login_required
def cocktail_lists():

    my_cocktail_list = db.execute("SELECT * FROM cocktail_lists WHERE user_id = ?", session["user_id"])
    my_cocktail_lists = db.execute("SELECT * FROM list_names WHERE user_id = ? AND category = 'cocktail'", session["user_id"])

    #flash(my_cocktail_list)
    return render_template("cocktail_lists.html", my_cocktail_list=my_cocktail_list, my_cocktail_lists=my_cocktail_lists)


@app.route("/create_list", methods=["GET", "POST"])
@login_required
def create_list():

    if request.method == "POST":
        category = "cocktail"
        list_name = request.form.get("list_name")

        db.execute("INSERT INTO list_names (user_id, category, name) VALUES(?,?,?)", session["user_id"], category, list_name)

        flash(list_name + " added to your cocktail lists!")
        return redirect("/cocktail_lists")

    return redirect("/cocktail_lists")

@app.route("/add_list", methods=["GET", "POST"])
@login_required
def add_list():

    #if request.method == "POST":
    #    cocktail_data = request.form.get("cocktail_data")

        #db.execute("INSERT INTO cocktail_lists (user_id, list_name, cocktail_id, cocktail_name, thumb_url) VALUES(?,?,?,?,?)", session["user_id"], cocktail_data["list_name"], cocktail_data["cocktail_id"], cocktail_data["cocktail_name"], cocktail_data["thumb_url"])
    cocktail_data = request.form.get(cocktail_data)

    flash(cocktail_data)
    #flash(cocktail_data["cocktail_name"] + " has been added to following list: "+cocktail_data["list_name"])
    return render_template("/cocktail_lists.html") # change this to return to cocktail_recipe
