from flask import Flask, render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import psycopg2

def get_conn():
    return psycopg2.connect(
        host = "localhost",
        port = 5433,
        database = "Store",
        user = "postgres",
        password = "postgres",
    )

# NOTE: This is a very good guide for postgresql on aws: https://medium.com/@rangika123.kanchana/how-to-configure-postgresql-17-on-amazon-linux-2023-da9426261620
# NOTE: I always forget,  but run screen to start screen session and screen -r to check current sessions on your aws instance.
app = Flask(__name__)
app.secret_key = "sixsevensixsevensixseven"

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/Store'

db=SQLAlchemy(app)

# Pages:
@app.route("/")
def index():
    username = session.get('name', None)
    if username == None:
        return redirect(url_for('login'))
    return render_template("index.html", name=username)

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
    return redirect(url_for('index'))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/cart")
def cart():
    return render_template("cart.html")

# Queries:
@app.route('/add_user', methods=['POST'])
def add_user():
    try:
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
        return redirect(url_for('index'))
    except psycopg2.errors.UniqueViolation:
        print("Dont copy someones homework homeboy")
        return redirect(url_for('register'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == "POST":
        uname= request.form["username"]
        passw= request.form["password"]
        conn = get_conn()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE name = %s', (uname,))
        user_record = cur.fetchone()
        if user_record:
            id, name, password, isadmin = user_record
            if str(password) == passw:
                session['id'] = id
                session['name'] = name
                return redirect (url_for('index'))
            return redirect (url_for('login')), 'Invalid Username or Password'
    return render_template("login.html")

# Main
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=4444)