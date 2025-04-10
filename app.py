from flask import Flask, request, redirect, render_template, session, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret_key"

DATABASE = "database.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            title TEXT,
            content TEXT,
            is_private INTEGER
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    user = session.get('username')
    
    if user:
        conn = get_db()
        c = conn.cursor()
        c.execute(f"SELECT * FROM notes WHERE user = '{user}'")
        notes = c.fetchall()
        conn.close()
    return render_template('index.html', user=user, notes=notes)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        c = conn.cursor()
        c.execute(f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')")
        conn.commit()
        conn.close()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        c = conn.cursor()
        c.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'")
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect('/')
        else:
            return 'Login failed.'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


@app.route('/note/new', methods=['GET', 'POST'])
def create_note():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        is_private = int('private' in request.form)

        conn = get_db()
        c = conn.cursor()
        c.execute(f'''
            INSERT INTO notes (user, title, content, is_private)
            VALUES ('{session["username"]}', '{title}', '{content}', {is_private})
        ''')
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('create_note.html')

@app.route('/note/<int:note_id>', methods=['GET', 'POST'])
def view_note(note_id):
    conn = get_db()
    c = conn.cursor()
    c.execute(f"SELECT * FROM notes WHERE id = {note_id}")
    note = c.fetchone()
    conn.close()
    
    user = session.get('username')

    if note is None:
        return "Note not found", 404
    
    if request.method == 'POST':
        if 'delete' in request.form:
            conn = get_db()
            c = conn.cursor()
            c.execute(f"DELETE FROM notes WHERE id = {note_id}")
            conn.commit()
            conn.close()
            return redirect('/')

    return render_template('view_note.html', note=note, user=user)

@app.route('/note/<int:note_id>/edit', methods=['GET', 'POST'])
def edit_note(note_id):
    

    conn = get_db()
    c = conn.cursor()
    c.execute(f"SELECT * FROM notes WHERE id = {note_id}")
    note = c.fetchone()

    if note is None:
        return "Note not found", 404

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        is_private = int('private' in request.form)

        c.execute(f'''
            UPDATE notes
            SET title = '{title}', content = '{content}', is_private = {is_private}
            WHERE id = {note_id}
        ''')
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('edit_note.html', note=note)

@app.route('/notes/')
def list_notes():
    conn = get_db()
    c = conn.cursor()
    notes = []
    
    if request.method == 'GET':
        if 'search' in request.args:
            search_query = request.args['q']
            c.execute(f"SELECT * FROM notes WHERE title LIKE '%{search_query}%' AND is_private = 0")
            notes = c.fetchall()
            conn.close()
            return render_template('list_notes.html', notes=notes, search_query=search_query)
        else :
            c.execute(f"SELECT * FROM notes WHERE is_private = 0")
            notes = c.fetchall()
            conn.close()

    return render_template('list_notes.html', notes=notes)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)