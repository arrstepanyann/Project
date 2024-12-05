import os
import sqlite3
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "supersecretkey"

def init_db():
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database', 'users.db')
    if not os.path.exists(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path))

    # Создаем или подключаемся к базе данных
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

def save_to_file(username, password):
    # Путь к файлу, где будут храниться логины и пароли
    file_path = r'C:\Project\login.txt'
    
    with open(file_path, 'a') as file:
        file.write(f"Логин: {username}, Пароль: {password}\n")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Путь к базе данных
        db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database', 'users.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            
            # Сохранение в файл
            save_to_file(username, password)
            
            return redirect('/login')
        except sqlite3.IntegrityError:
            return "Имя пользователя уже занято!"
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Путь к базе данных
        db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database', 'users.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = username
            
            # Сохранение в файл
            save_to_file(username, password)
            
            return redirect('/menu')
        else:
            return "Неверные данные для входа!"
    
    return render_template('login.html')

@app.route('/menu')
def menu():
    if 'username' not in session:
        return redirect('/login')

    return render_template('menu.html', username=session['username'])

if __name__ == "__main__":
    init_db()  # Инициализация базы данных при запуске
    app.run(debug=True)
