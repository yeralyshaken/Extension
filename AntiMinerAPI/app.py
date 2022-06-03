import json
from flask import Flask, request, session, redirect, url_for, render_template, flash, Response
import psycopg2
import psycopg2.extras
import re 
import requests
import bs4
from urllib.parse import urlparse
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

minerRegex = re.compile(r'coinhive.min.js|wpupdates.github.io/ping|cryptonight.asm.js|coin-hive.com|jsecoin.com|cryptoloot.pro|webassembly.stream|ppoi.org|xmrstudio|webmine.pro|miner.start|allfontshere.press|upgraderservices.cf|vuuwd.com')

@app.route('/blacklist', methods=['GET', 'POST'])
def blacklist():
    if 'loggedin' in session:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT url FROM blacklist")
        urls = cursor.fetchall()
        
        urls = [url[0] for url in urls]

        if request.method == 'POST':
            return Response(json.dumps(urls),  mimetype='application/json')
        
        return render_template('blacklist.html', urls=urls)

    return redirect(url_for('login'))

@app.route('/detect', methods=['GET', 'POST'])
def detect():
    if 'loggedin' in session:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        if request.method == 'POST' and 'url' in request.form:
            url_address = request.form['url']

            cursor.execute('SELECT * FROM blacklist WHERE %s ~ url or url ~ %s', (url_address, url_address))
            danger_url = cursor.fetchone()
            print(url_address)
            
            if danger_url:
                flash('URL already exists!')
            
            #scan
            else:
                try:
                    requests.packages.urllib3.disable_warnings()
                    if 'http' in url_address:
                        scansite = requests.get(url_address)
                    else:
                        scansite = requests.get('http://' + url_address)

                    scansite.raise_for_status()

                    scansite2 = bs4.BeautifulSoup(scansite.text, "html.parser")

                    final = scansite2.find("script", text=minerRegex)

                    if final:
                        cursor.execute("INSERT INTO blacklist (url) VALUES (%s)", (url_address))
                        conn.commit()
                        flash("{} added to blasklist!".format(url_address))
                    else:
                        flash('Could not find any problems!')
                except:
                    flash('Could not connect')
                    flash('Try to use correct url')
        elif request.method == 'POST':
            flash('Something wrong!')
        return render_template('detect.html')

    return redirect(url_for('login'))

@app.route('/')
def main_page():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return render_template('welcome.html')

@app.route('/home')
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