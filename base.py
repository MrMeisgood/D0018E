from flask import Flask, render_template, url_for, request as flask_request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import psycopg2
import requests

def get_conn():
    return psycopg2.connect(
        host = "localhost",
        port = 5432,
        database = "store",
        user = "postgres",
        password = "postgres",
    )

# NOTE: This is a very good guide for postgresql on aws: https://medium.com/@rangika123.kanchana/how-to-configure-postgresql-17-on-amazon-linux-2023-da9426261620
# NOTE: I always forget,  but run screen to start screen session and screen -r to check current sessions on your aws instance.
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/store'

db=SQLAlchemy(app)

# Pages:
@app.route("/")
def index():
    items = get_all_items()
    return render_template("index.html", items=items)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

# Queries:
@app.route('/add_user', methods=['POST'])
def add_user():
    uname= flask_request.form["username"]
    passw= flask_request.form["password"]

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users (name, password) VALUES (%s, %s)",
        (uname, passw)
    )

    conn.commit()
    cur.close()
    conn.close()
    return "User created!"

# Api 
# I kinda feel like it'll just be simpler to store the json locally
def get_all_items():
    url = "http://minecraft-ids.grahamedgecombe.com/items.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    # I feel like this is unnecessary, but I'll leave it for now.
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data =  response.json()
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