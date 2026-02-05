from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Function that's ran when accessing index page
@app.route("/")
def index():
    return render_template("index.html")

# Main
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=4444)