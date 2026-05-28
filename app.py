from flask import Flask, render_template, request, redirect, session
import psycopg2
import os

app = Flask(__name__)
app.secret_key = "agmidyouth_super_secret_key_2026"

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    DATABASE_URL = "postgresql://amazing_grace_user:D1WOsKyPA4J7jmlilzWFy8cYJqOUgQjO@dpg-d8bkn0ul51nc73e044ug-a.oregon-postgres.render.com/amazing_grace"



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

    return redirect('/success')

@app.route('/members')
def members():

    if not session.get('admin'):
        return redirect('/login')

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM members")
    members = cursor.fetchall()

    conn.close()

    return render_template('members.html', members=members)

@app.route('/delete/<int:id>')
def delete(id):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM members WHERE id = %s", (id,))

    conn.commit()
    conn.close()

    return redirect('/members')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']

        cursor.execute('''
            UPDATE members
            SET name=%s, age=%s
            WHERE id=%s
        ''', (name, age, id))

        conn.commit()
        conn.close()

        return redirect('/members')

    cursor.execute("SELECT * FROM members WHERE id=%s", (id,))
    member = cursor.fetchone()

    conn.close()

    return render_template('edit.html', member=member)

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        password = request.form['password']

        if password == "churchadmin":
            session['admin'] = True
            return redirect('/members')

    return '''
        <form method="POST">
            <input type="password" name="password">
            <button type="submit">Login</button>
        </form>
    '''
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/login')

@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == '__main__':
    app.run(debug=True)