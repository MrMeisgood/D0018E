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


# NOTE: This is a very good guide for postgresql on aws: https://medium.com/@rangika123.kanchana/how-to-configure-postgresql-17-on-amazon-linux-2023-da9426261620
# NOTE: I always forget,  but run screen to start screen session and screen -r to check current sessions on your aws instance.
app = Flask(__name__)
app.secret_key = "sixsevensixsevensixseven"

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@localhost/store"

db = SQLAlchemy(app)


# Pages:
@app.route("/")
def index():
    items = get_all_items()
    username = session.get("name", None)
    if not username:
        return redirect(url_for("login"))
    return render_template("index.html", name=username, items=items)


# @app.route("/home")
# def home():
#     username = session.get('name', None)
#     if username == None:
#         return redirect(url_for('login'))
#     return render_template("index.html", name=username)


@app.route("/logout")
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect(url_for("index"))


@app.route("/register")
def register():
    return render_template("register.html")


# Queries:
@app.route("/add_user", methods=["POST"])
def add_user():
    try:
        uname = flask_request.form["username"]
        passw = flask_request.form["password"]

        conn = get_conn()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users (name, password) VALUES (%s, %s)", (uname, passw)
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


# Api
# I kinda feel like it'll just be simpler to store the json locally
def get_all_items():
    url = "http://minecraft-ids.grahamedgecombe.com/items.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }
    # I feel like this is unnecessary, but I'll leave it for now.
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data
        elif response.status_code == 202:
            print("Proccessing... \n\n")
        else:
            response.raise_for_status()
            print("\n\n GUH!!! \n\n")
            break


# Main
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=4444)
