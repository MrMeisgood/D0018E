from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://temp.db"
# db = SQLAlchemy(app)

# Initial kladd databas config
# class Todo(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     content = db.Column(db.String(200), nullable=False)
#     completed = db.Column(db.Integer, default=0)
    # This is just here cause it might be good to have
    # date_created = db.Column(db.DateTime, default=datetime.UTC)

# def __repr__(self):
#     return "<Task %r>" % self.id

# Function that's ran when accessing index page
@app.route("/")
def index():
    return render_template("index.html")

# Main
if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()

    app.run(debug=True, host="0.0.0.0", port=4000)