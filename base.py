from flask import (
    Flask,
    render_template,
    request as flask_request,
    session,
    url_for,
    redirect,
)
from flask_sqlalchemy import SQLAlchemy

from connection_config import get_conn
import psycopg2
import requests
import random


# NOTE: This is a very good guide for postgresql on aws: https://medium.com/@rangika123.kanchana/how-to-configure-postgresql-17-on-amazon-linux-2023-da9426261620
# NOTE: I always forget,  but run screen to start screen session and screen -r to check current sessions on your aws instance.
app = Flask(__name__)
app.secret_key = "sixsevensixsevensixseven"

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@localhost/store"

db = SQLAlchemy(app)

# --- Pages ---
@app.route("/", methods=["GET", "POST"])
def index():
    items = return_n_random(product(), 30)
    username = session.get("name", None)
    if not username:
        return redirect(url_for("login"))
    if flask_request.method == "POST":
        try:
            item_id = flask_request.form.get("item_id", None)
            conn = get_conn()
            cur = conn.cursor()
            cur.execute(
            "SELECT item_id FROM cart"
            )
        except Exception:
            return "ERROR HERE"
    return render_template("index.html", name=username, items=items)


@app.route("/logout")
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect(url_for("index"))


@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/cart", methods=["GET","POST"])
def cart():
    return render_template("cart.html")

# --- Queries ---
@app.route("/add_user", methods=["POST"])
def add_user():
    try:
        uname = flask_request.form["username"]
        passw = flask_request.form["password"]

        conn = get_conn()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)", (uname, passw)
        )

        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("index"))
    except psycopg2.errors.UniqueViolation:
        print("Dont copy someones homework homeboy")
        return redirect(url_for("register"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if flask_request.method == "POST":
        uname = flask_request.form["username"]
        passw = flask_request.form["password"]
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (uname,))
        user_record = cur.fetchone()
        if user_record:
            id, name, password, isadmin = user_record
            if str(password) == passw:
                session["id"] = id
                session["name"] = name
                return redirect(url_for("index"))
            return redirect(url_for("login")), "Invalid Username or Password"
    return render_template("login.html")

# --- Helpers ---
# Funciton used for filling the products table.
def initial_insert():
    with open("static/products.txt", "r") as file:
        query = file.read()

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    cur.close()
    conn.close()

# Get's all items and their corresponding names from the api below.
def get_items():
    url = "http://minecraft-ids.grahamedgecombe.com/items.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return data

# Takes an array and returns n random items of the initial array.
def return_n_random(array, n):
    return random.sample(array, min(n, len(array)))

# Fetches all products from database
def product():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM products"
        )
        prod_records = cur.fetchall()
        return prod_records
    except Exception:
        return "ERROR at PRODUCT"

# Used to convert the api request to a query 
def convert():
    query = "INSERT INTO products (ptype, pmeta, pname) VALUES"
    data = get_items()
    for item in data:
        query += "("
        for key, value in item.items():
            if key == "name":
                query += "'" + str(value).replace("'","''") + "'"
            elif key != "text_type":
                query += str(value) + ", "
        query = query + "),\n"
    query = query[:-2] + ";"
    with open('static/products.txt', "w") as file:
        file.write(query)

# Main
if __name__ == "__main__":
    # convert()
    # initial_insert()
    app.run(debug=True, host="0.0.0.0", port=4444)
