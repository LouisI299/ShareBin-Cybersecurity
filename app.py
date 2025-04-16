from flask import Flask, request, redirect, render_template, session, url_for, flash, jsonify, send_from_directory
import sqlite3
import os
from werkzeug.utils import secure_filename
import requests



app = Flask(__name__)
app.secret_key = "secret_key"

DATABASE = "database.db"
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'mp4', 'avi', 'mov', 'mkv', 'mp3', 'wav', 'ogg', 'pdf', 'doc', 'docx', 'txt' }
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  

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
            password TEXT,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            title TEXT,
            content TEXT,
            is_private INTEGER,
            file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS friend_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_id INTEGER,
            status TEXT CHECK(status IN ('pending', 'accepted', 'declined')),
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(sender_id) REFERENCES users(id),
            FOREIGN KEY(receiver_id) REFERENCES users(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            user_id INTEGER,
            friend_id INTEGER,
            UNIQUE(user_id, friend_id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(friend_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()
    
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    user = session.get('username')
    notes = []
    
    if user:
        conn = get_db()
        c = conn.cursor()
        c.execute(f"SELECT * FROM users WHERE username = '{user}'")
        valid_user = c.fetchone()
        if not valid_user:
            session.pop('username', None)  # Clear invalid session
            user = None
        else:
            c.execute(f"SELECT * FROM notes WHERE user = '{user}'")
            notes = c.fetchall()
        conn.close()
    return render_template('index.html', user=user, notes=notes)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'login' in request.form:
            username = request.form['username']
            password = request.form['password']
            conn = get_db()
            c = conn.cursor()
            c.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'")
            user = c.fetchone()
            conn.close()
            if user:
                session['username'] = username
                session['user_id'] = user[0]
                return redirect('/')
            else:
                return 'Login failed.'
        elif 'register' in request.form:
            email = request.form['email']
            username = request.form['username']
            password = request.form['password']
            conn = get_db()
            c = conn.cursor()
            c.execute(f"SELECT * FROM users WHERE username = '{username}'")
            existing_user = c.fetchone()
            if existing_user:
                return 'Username already exists.'
            c.execute(f"SELECT * FROM users WHERE email = '{email}'")
            existing_email = c.fetchone()
            if existing_email:
                return 'Email already exists.'
            if not username or not password:
                return 'Username and password are required.'
            if not email:
                return 'Email is required.'
            c.execute(f'''
                INSERT INTO users (username, password, email)
                VALUES ('{username}', '{password}', '{email}')
            ''')
            conn.commit()
            conn.close()
            session['username'] = username
            return redirect('/')
    return render_template('login.html', user=session.get('username'))

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
        file = request.files.get('file')
        is_private = int('private' in request.form)
        filename = None
        if file and file.filename != '':
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        conn = get_db()
        c = conn.cursor()
        c.execute(f'''
            INSERT INTO notes (user, title, content, is_private, file_path)
            VALUES ('{session["username"]}', '{title}', '{content}', {is_private}, '{filename}')
        ''')
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('create_note.html', user=session.get('username'))

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

    return render_template('edit_note.html', note=note, user=session.get('username'))

@app.route('/notes/')
def list_notes():
    conn = get_db()
    c = conn.cursor()
    notes = []
    mynotes = []
    if 'username' in session:
        user = session.get('username')
        c.execute(f"SELECT * FROM notes WHERE user = '{user}'")
        mynotes = c.fetchall()
        
        

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

    return render_template('list_notes.html', notes=notes, user=session.get('username'), mynotes=mynotes)

@app.route('/profile/')
def profile():
    user = session.get('username')
    if not user:
        return redirect('/login')

    conn = get_db()
    c = conn.cursor()
    c.execute(f"SELECT * FROM users WHERE username = '{user}'")
    user_info = c.fetchone()
    conn.close()

    return render_template('profile.html', user=user, user_info=user_info)

@app.route('/admin')
def admin_dashboard():
    if 'username' not in session:
        return redirect('/login')

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()

    c.execute("SELECT * FROM notes")
    notes = c.fetchall()

    conn.close()

    return render_template('admin.html', users=users, notes=notes, user=session.get('username'))

@app.route('/about')
def about():
    return render_template('about.html', user=session.get('username'))
@app.route('/contact')
def contact():
    return render_template('contact.html', user=session.get('username'))

@app.route("/friend-request/<int:friend_id>", methods=["POST"])
def send_friend_request(friend_id):
    requestor_id = session.get('user_id')
    receiver_id = friend_id
    if not requestor_id:
        return jsonify({"error": "User not logged in"}), 401
    conn = get_db()
    c = conn.cursor()
    c.execute(f"SELECT * FROM friend_requests WHERE sender_id = {requestor_id} AND receiver_id = {receiver_id}")
    existing_request = c.fetchone()
    if existing_request:
        return jsonify({"error": "Friend request already sent"}), 400
    c.execute(f'''
        INSERT INTO friend_requests (sender_id, receiver_id, status)
        VALUES ({requestor_id}, {friend_id}, 'pending')
    ''')
    conn.commit()
    conn.close()
    return redirect('/social')

@app.route("/respond-friend-request/<int:request_id>", methods=["POST"])
def respond_friend_request(request_id):
    action = request.form.get('action')
    conn = get_db()
    c = conn.cursor()
    c.execute(f"SELECT * FROM friend_requests WHERE id = {request_id}")
    request_data = c.fetchone()
    if not request_data:
        return jsonify({"error": "Friend request not found"}), 404
    if action == 'accept':
        c.execute(f'''
            UPDATE friend_requests
            SET status = 'accepted'
            WHERE id = {request_id}
        ''')
        c.execute(f'''
            INSERT INTO friends (user_id, friend_id)
            VALUES ({request_data[1]}, {request_data[2]})
        ''')
    elif action == 'decline':
        c.execute(f'''
            UPDATE friend_requests
            SET status = 'declined'
            WHERE id = {request_id}
        ''')
    conn.commit()
    conn.close()
    return jsonify({"message": "Friend request responded to"}), 200

@app.route("/social", methods=["GET"])
def social():
    if 'username' not in session:
        return redirect('/login')

    conn = get_db()
    c = conn.cursor()
    c.execute(f"SELECT * FROM friend_requests WHERE receiver_id = {session['user_id']} AND status = 'pending'")
    pending_requests = c.fetchall()

    c.execute(f"SELECT * FROM friends WHERE user_id = {session['user_id']}")
    friends = c.fetchall()
    
    if request.method == 'GET':
        if 'search' in request.args:
            search_query = request.args['q']
            c.execute(f"SELECT * FROM users WHERE username LIKE '%{search_query}%'")
            users = c.fetchall()
            conn.close()
            return render_template('social.html', pending_requests=pending_requests, friends=friends, users=users, search_query=search_query, user=session.get('username'))
        

    conn.close()

    return render_template('social.html', pending_requests=pending_requests, friends=friends, user=session.get('username'))


    


if __name__ == '__main__':
    init_db()
    app.run(debug=True)