from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
from passlib.hash import pbkdf2_sha256
from flask_security.utils import verify_password
import MySQLdb.cursors
import re
import passlib


app = Flask(__name__)

app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'socialuser'
app.config['MYSQL_PASSWORD'] = 'socialpass'
app.config['MYSQL_DB'] = 'social'

mysql = MySQL(app)


@app.route('/social/', methods=['GET', 'POST'])
def login():

    msg = ''
    
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
      
        username = request.form['username']
        password = request.form['password']
     
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username))
        account = cursor.fetchone()
     
       
        if account:
            test_hash = pbkdf2_sha256.verify(password, account['password'])
           
            if pbkdf2_sha256.verify(password, account['password']):
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
            
                return redirect(url_for('home'))
            else:
                msg = test_hash,'####', password,'####', account['password']
        else:
        
            msg = 'Неверный логин или пароль!'
   
   
    return render_template('index.html', msg=msg)

@app.route('/social/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login'))

@app.route('/social/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        name = request.form['name']
        surname = request.form['surname']
        age = request.form['age']
        gender = request.form['gender']
        interest = request.form['interest']
        city = request.form['city']


        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
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
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (username, pwd_hash, email, name, surname, age, gender, interest, city,))
            mysql.connection.commit()
            msg = 'Вы успешно зарегестрировались!'

    
    elif request.method == 'POST':
          msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

@app.route('/social/home')
def home():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts LEFT JOIN friends  ON accounts.id =  friends.friend_id WHERE friends.account_id =  %s', (session['id'],))
        friends = cursor.fetchall()
        return render_template('home.html', account=account, friends=friends)
    return redirect(url_for('login'))
    

@app.route('/social/profile')
def profile():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))

@app.route('/social/displaypeople')
def displaypeople():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT id,username, name , surname, email  FROM accounts where username != %s', (session['username']),)
        account = cursor.fetchall()
        return render_template('displaypeople.html', account=account)
    return redirect(url_for('login'))


    
@app.route('/social/displayman', methods=['GET'])
def displayman():
    if 'loggedin' in session:
        user_id = request.args.get('user_id') 
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts where id = %s',   [user_id])
        account = cursor.fetchone()
        return render_template('displayman.html', account=account)
    return redirect(url_for('login'))

@app.route('/social/displayfriend', methods=['GET'])
def displayfriend():
    if 'loggedin' in session:
        user_id = request.args.get('user_id') 
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts where id = %s',   [user_id])
        account = cursor.fetchone()
        return render_template('displayfriend.html', account=account)
    return redirect(url_for('login'))

@app.route('/social/addfriend', methods=['POST'])
def addfriend():
    if 'loggedin' in session:
       if request.method == 'POST': 
            friend_id = request.form.get('friend_id')
            friend_name = request.form.get('friend_name')
            friend_surname = request.form.get('friend_surname')
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT *  FROM friends where account_id = %s and friend_id = %s', (session['id'], friend_id ))
            friend = cursor.fetchone()
            if friend:
                return "Этот человек уже у вас в друзьях!"
            else: 
                cursor.execute('INSERT INTO friends ( account_id, friend_id )   VALUES(%s, %s) ', (session['id'], friend_id ),)
                mysql.connection.commit()
                return render_template('addfriend.html', friend_name=friend_name, friend_surname=friend_surname)
    return redirect(url_for('login')) 
