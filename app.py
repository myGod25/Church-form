from flask import Flask, render_template, request
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

# Create database and table
def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id SERIAL PRIMARY KEY,
            name TEXT,
            age INTEGER,
            phone TEXT,
            whatsapp TEXT,
            email TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    age = request.form['age']
    phone = request.form['phone_number']
    whatsapp = request.form['whatsapp_number']
    email = request.form['email']

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO members (name, age, phone, whatsapp, email)
        VALUES (%s, %s, %s, %s, %s)
    ''', (name, age, phone, whatsapp, email))

    conn.commit()
    conn.close()

    return f"Thank you {name}, your data has been saved!"

if __name__ == '__main__':
    app.run(debug=True)