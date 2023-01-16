from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, cocktail_lu, recipe_lu


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

    cocktail = recipe_lu(request.args.get("idDrink"))
    
    return render_template("cocktail_recipe.html", cocktail=cocktail)