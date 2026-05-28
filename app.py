from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import os

print("Flask app is starting...")

app = Flask(__name__)
app.secret_key = "agmidyouth_super_secret_key_2026"

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    DATABASE_URL = "postgresql://amazing_grace_user:D1WOsKyPA4J7jmlilzWFy8cYJqOUgQjO@dpg-d8bkn0ul51nc73e044ug-a.oregon-postgres.render.com/amazing_grace"


# Create database and table
def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id SERIAL PRIMARY KEY,
            name TEXT,
            age INTEGER,
            phone TEXT,
            whatsapp TEXT,
            email TEXT,
            gender TEXT,
            born_again TEXT,
            previous_attendance TEXT,
            heard_about_us TEXT,
            preferred_contact TEXT,
            workforce_interest TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    age = request.form.get("age")
    phone = request.form.get("phone_number")
    whatsapp = request.form.get("whatsapp_number")
    email = request.form.get("email")
    gender = request.form.get("gender")
    born_again = request.form.get("born_again")
    previous_attendance = request.form.get("previous_attendance")
    heard_about_us = request.form.get("heard_about_us")
    preferred_contact = request.form.get("preferred_contact")
    workforce_interest = request.form.get("workforce_interest")

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute(
    """
    INSERT INTO members (
        name, age, phone, whatsapp, email,
        gender, born_again, previous_attendance,
        heard_about_us, preferred_contact, workforce_interest
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
""",
    (
        name, age, phone, whatsapp, email,
        gender, born_again, previous_attendance,
        heard_about_us, preferred_contact, workforce_interest
    ),
)
    conn.commit()
    conn.close()

    return redirect("/success")

@app.route('/members')
def members():

    if not session.get("admin"):
        return redirect("/login")

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM members ORDER BY id DESC")
    members = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM members")
    total = cursor.fetchone()[0]

    conn.close()

    return render_template("admin.html", members=members, total=total)

@app.route("/delete/<int:id>")
def delete(id):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM members WHERE id = %s", (id,))

    conn.commit()
    conn.close()

    return redirect("/members")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]

        cursor.execute(
            """
            UPDATE members
            SET name=%s, age=%s
            WHERE id=%s
        """,
            (name, age, id),
        )

        conn.commit()
        conn.close()

        return redirect("/members")

    cursor.execute("SELECT * FROM members WHERE id=%s", (id,))
    member = cursor.fetchone()

    conn.close()

    return render_template("edit.html", member=member)

@app.route("/login", methods=["GET", "POST"])
def login():
    
    hashed_password = "scrypt:32768:8:1$0YwnQBTs1sFfM2iv$6e9b518b7beb02699679b1afca5c188010c62d2394110e1e58b7bcb723268088aeed2c13e7e8fa0334680830d348cc5c2724fef8de0683ac896073327b6a62f1"

    if request.method == "POST":

        password = request.form["password"]
        
        if check_password_hash(hashed_password, password):
            session["admin"] = True
            return redirect("/members")

    return """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Login</title>

    <style>
        body {
            font-family: Arial;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }

        .login-box {
            background: white;
            padding: 35px;
            border-radius: 12px;
            width: 320px;
            text-align: center;
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        }

        h2 {
            color: #2a5298;
            margin-bottom: 20px;
        }

        input[type="password"] {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ccc;
            border-radius: 6px;
        }

        button {
            width: 100%;
            padding: 12px;
            background: #2a5298;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
        }

        button:hover {
            background: #1e3c72;
        }
    </style>
</head>

<body>

<div class="login-box">
    <h2>🔐 Admin Login</h2>

    <form method="POST">
        <input type="password" name="password" placeholder="Enter password" required>
        <button type="submit">Login</button>
    </form>

</div>

</body>
</html>
"""


@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/login")


@app.route("/success")
def success():
    return render_template("success.html")


if __name__ == "__main__":
    app.run(debug=True)
