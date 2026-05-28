from flask import Flask, render_template, request, redirect, session
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
    name = request.form["name"]
    age = request.form["age"]
    phone = request.form["phone_number"]
    whatsapp = request.form["whatsapp_number"]
    email = request.form["email"]
    gender = request.form["gender"]
    born_again = request.form["born_again"]
    previous_attendance = request.form["previous_attendance"]
    heard_about_us = request.form["heard_about_us"]
    preferred_contact = request.form["preferred_contact"]
    workforce_interest = request.form["workforce_interest"]

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

@app.route('/update-db')
def update_db():

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
        ALTER TABLE members
        ADD COLUMN IF NOT EXISTS gender TEXT,
        ADD COLUMN IF NOT EXISTS born_again TEXT,
        ADD COLUMN IF NOT EXISTS previous_attendance TEXT,
        ADD COLUMN IF NOT EXISTS heard_about_us TEXT,
        ADD COLUMN IF NOT EXISTS preferred_contact TEXT,
        ADD COLUMN IF NOT EXISTS workforce_interest TEXT
    """)

    conn.commit()
    conn.close()

    return "Database updated successfully!"


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        password = request.form["password"]

        if password == "churchadmin":
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
