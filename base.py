from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import psycopg2

def get_conn():
    return psycopg2.connect(
        host = "localhost",
        port = 5433,
        database = "store",
        user = "postgres",
        password = "postgres",
    )

# NOTE: This is a very good guide for postgresql on aws: https://medium.com/@rangika123.kanchana/how-to-configure-postgresql-17-on-amazon-linux-2023-da9426261620
# NOTE: I always forget,  but run screen to start screen session and screen -r to check current sessions on your aws instance.
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/Store'

db=SQLAlchemy(app)

# Pages:
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

# Queries:
@app.route('/add_user', methods=['POST'])
def add_user():
    uname= request.form["username"]
    passw= request.form["password"]

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

# Main
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=4444)