from flask import Flask, render_template

app = Flask(__name__)

# Function that's ran when accessing index page
@app.route("/")
def index():
    return render_template("index.html")

# Main
if __name__ == "__main__":
    app.run(debug=True)