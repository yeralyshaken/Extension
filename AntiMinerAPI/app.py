from flask import Flask, request, session, redirect, url_for, render_template, flash
import psycopg2
import psycopg2.extras
import re 
from werkzeug.security import generate_password_hash, check_password_hash
# import uuid
 
app = Flask(__name__)
app.secret_key = 'ae11e0007d644e9193d39a49ec3878d1' # uuid.uuid4().hex
# print(app.secret_key)

DB_HOST = "localhost"
DB_NAME = "antiminer"
DB_USER = "postgres"
DB_PASS = "123321azaz"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

@app.route('/detect', methods=['GET', 'POST'])
def detect():
    if 'loggedin' in session:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        if request.method == 'POST' and 'url' in request.form:
            url_address = request.form['url']

            cursor.execute('SELECT * FROM blacklist WHERE url = %s', (url_address,))
            danger_url = cursor.fetchone()
            print(danger_url)
            
            if danger_url:
                flash('URL already exists!')
            else:
                cursor.execute("INSERT INTO blacklist (url) VALUES (%s)", (url_address))
                conn.commit()
                flash('Done!')
                return render_template('home.html')
        elif request.method == 'POST':
            flash('Something wrong!')
        return render_template('home.html')

    return redirect(url_for('login'))


@app.route('/')
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))
 
@app.route('/login/', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        print(password)
 
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
 
        if account:
            password_rs = account['password']
            print(password_rs)
            if check_password_hash(password_rs, password):
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                
                return redirect(url_for('home'))
            else:
                flash('Incorrect username/password')
        else:
            flash('Incorrect username/password')
 
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
    
        _hashed_password = generate_password_hash(password)
 
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        print(account)
        
        if account:
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only characters and numbers!')
        elif not username or not password or not email:
            flash('Please fill out the form!')
        else:
            cursor.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s,%s,%s,%s)", (fullname, username, _hashed_password, email))
            conn.commit()
            flash('You have successfully registered!')
            return render_template('login.html')
    elif request.method == 'POST':
        flash('Please fill out the form!')
    return render_template('register.html')


@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login'))

@app.route('/profile')
def profile(): 
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()

        return render_template('profile.html', account=account)
    
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)