from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from passlib.hash import pbkdf2_sha256
from flask_security.utils import verify_password
import MySQLdb.cursors
import re
import passlib


app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'socialuser'
app.config['MYSQL_PASSWORD'] = 'socialpass'
app.config['MYSQL_DB'] = 'social'

# Intialize MySQL
mysql = MySQL(app)

# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests
@app.route('/social/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
         # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username))
        account = cursor.fetchone()
     
       
        if account:
            test_hash = pbkdf2_sha256.verify(password, account['password'])
            # Create session data, we can access this data in other routes
            if pbkdf2_sha256.verify(password, account['password']):
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
            # Redirect to home page
                return redirect(url_for('home'))
            else:
                msg = test_hash,'####', password,'####', account['password']
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Неверный логин или пароль!'
      # Show the login form with message (if any)
   
    return render_template('index.html', msg=msg)

@app.route('/social/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/social/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        name = request.form['name']
        surname = request.form['surname']
        age = request.form['age']
        gender = request.form['gender']
        interest = request.form['interest']
        city = request.form['city']

    
    # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Аккаунт уже существует!'

         
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Неправильный email адрес!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Логин должен состоять только из букв и цифр!'
        elif not username or not password or not email:
            msg = 'Введите логин и пароль!'
        else:
            pwd_hash =  pbkdf2_sha256.hash(password)
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (username, pwd_hash, email, name, surname, age, gender, interest, city,))
            mysql.connection.commit()
            msg = 'Вы успешно зарегестрировались!'

    
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

@app.route('/social/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # User is loggedin show them the home page
        return render_template('home.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
    

@app.route('/social/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/social/displaypeople')
def displaypeople():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT id,username, name , surname, email  FROM accounts where username != %s', (session['username']),)
        account = cursor.fetchall()
        #account.extend(cur.fetchall())
        return render_template('displaypeople.html', account=account)
    return redirect(url_for('login'))


    
@app.route('/social/displayman')
def displayman():
    if 'loggedin' in session:
        username = request.args.get('username') 
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT id,username, name , surname, email  FROM accounts where username = %s', (username),)
        account = cursor.fetchone()
        return render_template('displayman.html', account=account)
    return redirect(url_for('login'))

@app.route('/social/addfriend', methods=['GET', 'POST'])
def addfriend():
    #  if 'loggedin' in session:
     req_data = request.get_json()
     friend_id = req_data['friend_id']
     return friend_id
     #return redirect(url_for('login'))