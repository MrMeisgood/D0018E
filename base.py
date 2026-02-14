from flask import Flask, render_template, url_for, request, redirect
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

# NOTE: I always forget,  but run screen to start screen session and screen -r to check current sessions on your aws instance.
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/Store'

db=SQLAlchemy(app)


# Function that's ran when accessing index page
@app.route("/")
def index():
    return render_template("index.html")


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