import random

import psycopg2
import requests
from flask import (
    Flask,
    redirect,
    render_template,
    session,
    url_for,
)
from flask import (
    request as flask_request,
)
from flask_sqlalchemy import SQLAlchemy

from connection_config import get_conn

# Constants
LOWEST_PRICE = 1
HIGHEST_PRICE = 50
# Please note that the max for this one is 719
DISPLAYED_ITEMS = 30

# NOTE: I always forget,  but run screen to start screen session and screen -r to check current sessions on your aws instance.
app = Flask(__name__)
app.secret_key = "sixsevensixsevensixseven"

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@localhost/store"

db = SQLAlchemy(app)


# --- Pages ---
@app.route("/", methods=["GET", "POST"])
def index():
    username = session.get("name", None)
    if not username:
        return redirect(url_for("login"))
    if flask_request.method == "POST":
        if flask_request.form.get("remove"):
            product_id = flask_request.form.get("remove", None)
            print(product_id)
            # Connect to database
            conn = get_conn()
            cur = conn.cursor()
            cur.execute(
                "UPDATE products SET is_active = 0 WHERE product_id = %s",
                (product_id, ),
            )
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for("index"))
        else:
            try:
                product_id = flask_request.form.get("item_id", None)
                # Connect to database
                conn = get_conn()
                cur = conn.cursor()
                # Get user_id (note that we expect the user to be signed in)
                user_id = session.get("id", None)
                # Check if product already exists in in_cart
                cur.execute(
                    "SELECT * FROM in_cart WHERE product_id = %s AND user_id = %s",
                    (product_id, user_id),
                )
                test = cur.fetchone()
                # Adds to in_cart or increases quantity
                if test:
                    cur.execute(
                        "UPDATE in_cart SET quantity = quantity + 1 WHERE product_id = %s AND user_id = %s",
                        (product_id, user_id),
                    )
                else:
                    cur.execute(
                        "INSERT INTO in_cart (user_id, product_id, quantity) VALUES (%s, %s, 1);",
                        (user_id, product_id),
                    )
                conn.commit()
                cur.close()
                conn.close()
            except Exception:
                return "The database be strugglin'"
    # Doesn't get items till we actually know they're needed [:DISPLAYED_ITEMS]
    is_admin = session.get("is_admin", None)
    items = get_products()
    if is_admin:
        return render_template("admin_index.html", name=username, items=items)
    return render_template("index.html", name=username, items=items)


@app.route("/logout")
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect(url_for("index"))


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/cart", methods=["GET", "POST"])
def cart():
    username = session.get("name", None)
    user_id = session.get("id", None)
    conn = get_conn()
    cur = conn.cursor()

    if flask_request.method == "POST":
        product_id = flask_request.form.get("remove", None)
        print(product_id)
        cur.execute(
            "DELETE FROM in_cart WHERE product_id = %s AND user_id = %s",
            (product_id, user_id),
        )
        conn.commit()

    cur.execute(
        """
        SELECT
            p.ptype AS ptype,
            p.pmeta AS pmeta,
            p.pname AS pname,
            i.quantity * p.price AS total_price,
            i.quantity AS quantity,
            p.product_id AS product_id
        FROM in_cart i
        JOIN products p ON p.product_id = i.product_id
        WHERE i.user_id = %s
    """,
        (user_id,),
    )
    # All my homies hate JOIN statements, this is an array containing: ptype, pmeta, pname, price * quantity, quantity, product_id.
    product_array = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("cart.html", username=username, product_array=product_array)


# for admin page to add products
@app.route("/admin_view", methods=["POST", "GET"])
def admin_view():
    username = session.get("name", None)
    conn = get_conn()
    cur = conn.cursor()
    if flask_request.method == "POST":
        pname = flask_request.form.get("name", None)
        price = flask_request.form.get("price", None)
        img_type = flask_request.form.get("type", None)
        cur.execute(
            """
            INSERT into products
            (pname, price, ptype, pmeta)
            VALUES (%s, %s, %s, 0)
        """,
            (pname, price, img_type),
        )
        conn.commit()
        return redirect(url_for("index"))
    return render_template("admin_view.html", username=username)


@app.route("/admin_review", methods=["POST", "GET"])
def admin_review():
    conn = get_conn()
    cur = conn.cursor()
    if flask_request.method == "POST":
        review_id = flask_request.form.get("remove", None)
        cur.execute(
            "DELETE FROM reviews WHERE review_id = %s",
            (review_id,),
        )
        conn.commit()
    cur.execute(
    """
        SELECT
            p.pname, 
            p.ptype,
            p.pmeta,
            r.rating,
            r.review,
            u.username,
            p.product_id,
            r.review_id
        FROM reviews r
        JOIN users u ON u.user_id = r.reviewer_id
        JOIN products p ON p.product_id = r.product_id
    """
    )
    review_array = cur.fetchall()
    return render_template("admin_review.html", review_array=review_array)


@app.route("/reviews/<int:product_id>", methods=["GET", "POST"])
def review(product_id):
    username = session.get("name", None)
    conn = get_conn()
    cur = conn.cursor()

    if flask_request.method == "POST":
        # Get user_id (note that we expect the user to be signed in)
        user_id = session.get("id", None)
        review = flask_request.form.get("review", None)
        rating = int(flask_request.form.get("rating", None))
        cur.execute(
            """
            INSERT into reviews
            (review, rating, reviewer_id, product_id)
            VALUES (%s, %s, %s, %s)
        """,
            (review, rating, user_id, product_id),
        )
        conn.commit()
    # This works now
    # NOTE: We need to add things like ptype, ptmeta and such to see images.
    cur.execute(
        """
        SELECT
            p.pname AS product_name, 
            p.ptype AS ptype,
            p.pmeta AS pmeta,
            r.rating,
            r.review,
            u.username AS reviewer_name,
            p.ptype AS ptype,
            p.pmeta AS pmeta
        FROM reviews r
        JOIN users u ON u.user_id = r.reviewer_id
        JOIN products p ON p.product_id = r.product_id
        WHERE r.product_id = %s
    """,
        (product_id,),
    )
    # Array containing: product_name, ptype, pmeta, rating, review, reviewer_name.
    review_array = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("review.html", review_array=review_array, username=username)


@app.route("/history")
def history():
    username = session.get("name", None)
    user_id = session.get("id", None)
    conn = get_conn()
    cur = conn.cursor()
    # NOTE: This query needs to be rewritten, I'm tired, so we'll do it together later
    # (unless you've solved it when I wake up)
    # cur.execute(
    #     """
    #     SELECT
    #         p.ptype,
    #         p.pmeta,
    #         p.pname,
    #         ci.quantity,
    #         p.price * ci.quantity
    #     FROM checkout c
    #     JOIN checkout_items ci ON ci.checkout_id = c.checkout_id
    #     JOIN products p ON p.product_id = ci.product_id
    #     WHERE c.user_id = %s
    # """,
    #     (user_id,),
    # )

    cur.execute("SELECT checkout_id FROM checkout WHERE user_id = %s", (user_id,))
    checkout_ids = cur.fetchall()
    history_array = []
    for id in checkout_ids:
        cur.execute(
            """
                SELECT 
                    p.ptype,
                    p.pmeta,
                    p.pname,
                    ci.quantity,
                    p.price * ci.quantity
                FROM checkout_items ci
                JOIN products p ON p.product_id = ci.product_id
                WHERE ci.checkout_id = %s
        """,
            (id,),
        )
        history_array.append(cur.fetchall())

    # Fetch total price
    cur.execute("SELECT total_price from checkout WHERE user_id = %s", (user_id,))
    total_price = cur.fetchall()
    # Array containing: ptype, pmeta, pname, quantity, item price,
    cur.close()
    conn.close()
    print(total_price)
    return render_template(
        "history.html",
        history_array=history_array,
        username=username,
        total_price=total_price,
    )


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
            id, name, password, is_admin = user_record
            if str(password) == passw:
                session["id"] = id
                session["name"] = name
                session["is_admin"] = is_admin
                return redirect(url_for("index"))
            return redirect(url_for("login"))
    return render_template("login.html")


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


# Moves the users active items to inactive
@app.route("/checkout")
def checkout():
    user_id = session.get("id", None)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM in_cart WHERE user_id = %s",
        (user_id,),
    )
    test = cur.fetchone()
    # Magical query, it creates a new checkout and also copies the values from the active
    # users in_cart to checkout_items.
    if test:
        cur.execute(
            """
            WITH new_checkout AS (
                INSERT INTO checkout (user_id) VALUES (%s) RETURNING checkout_id
            )
            INSERT INTO checkout_items (checkout_id, product_id, quantity)
            SELECT n.checkout_id, i.product_id, i.quantity
            FROM in_cart i
            JOIN products p ON p.product_id = i.product_id
            CROSS JOIN new_checkout n
            WHERE i.user_id = %s
        """,
            (user_id, user_id),
        )
        # Clear the users cart.
        cur.execute("DELETE FROM in_cart WHERE user_id = %s", (user_id,))
        # Calculate the total price and add it to checkout.
        # NOTE: This could probably be done in the first query, but we'll figure that out later
        # to avoid flabbergasting me completely!
        cur.execute(
            # NOTE: The total price is the sum of all ci.quantity * p.price.
            """
            UPDATE checkout c 
            SET total_price = (
                SELECT SUM(ci.quantity * p.price)
                FROM checkout_items ci
                JOIN products p ON p.product_id = ci.product_id
                WHERE ci.checkout_id = c.checkout_id
            )
            WHERE user_id = %s
        """,
            (user_id,),
        )

    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("history"))


# --- Helpers ---
# Funciton used for filling the products table.
def initial_insert():
    # Uses products.txt as a starting point
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


# NOTE: Outdated! Doesn't remove the unused items.
# Used to convert the api request to a query
def generate_products():
    query = "INSERT INTO products (ptype, pmeta, pname, price) VALUES"
    data = get_items()
    for item in data:
        query += "("
        for key, value in item.items():
            if key == "name":
                query += (
                    "'"
                    + str(value).replace("'", "''")
                    + "', "
                    + str(random.randint(LOWEST_PRICE, HIGHEST_PRICE))
                )
            elif key != "text_type":
                query += str(value) + ", "
        query = query + "),\n"
    query = query[:-2] + ";"
    with open("static/products.txt", "w") as file:
        file.write(query)


# Fetches all products from database
def get_products():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT product_id, ptype, pmeta, pname, price FROM products WHERE is_active = 1"
        )
        prod_records = cur.fetchall()
        return prod_records
    except Exception:
        return "ERROR at PRODUCT"


# Main
if __name__ == "__main__":
    # initial_insert()
    app.run(debug=True, host="0.0.0.0", port=4444)
