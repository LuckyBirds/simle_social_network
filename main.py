from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
#from flask_mysqldb import MySQL
import pymysql

from passlib.hash import pbkdf2_sha256
from flask_security.utils import verify_password

from flask_wtf import FlaskForm
from wtforms import Form, StringField, TextAreaField, SelectField, validators, ValidationError, TextField, TextAreaField, SubmitField, IntegerField, PasswordField, DateField
from wtforms.validators import DataRequired, Email

import time

#import MySQLdb.cursors
import json
import re
import passlib

from datetime import datetime




app = Flask(__name__)


app.config['SECRET_KEY'] = 'you-will-never-guess'

#app.config['MYSQL_HOST'] = '172.20.160.200'
#app.config['MYSQL_USER'] = 'socialuser'
#app.config['MYSQL_PASSWORD'] = 'socialpass'
#app.config['MYSQL_DB'] = 'social'
#app.config['MYSQL_PORT'] = 3306


#mysql = MySQL(app)


mysql_master = {
    "host": "172.20.160.200",
    "port": 3306,
    "user": "socialuser",
    "passwd": "socialpass",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "database": "social"
}

mysql_slave = {
    "host": "127.0.0.1",
    "port": 3307,
    "user": "socialuser",
    "passwd": "socialpass",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "database": "social"
}

conn = pymysql.connect(**mysql_master)
cursor = conn.cursor()

#import pdb; pdb.set_trace()

class AddFriendForm(FlaskForm):
    submit = SubmitField("Добавить в друзья")

class ChatForm(FlaskForm):
    chat_text = TextAreaField("Chat text", validators=[DataRequired()]) 
    submit = SubmitField("Написать другу")

class NewsForm(FlaskForm):
    news_text = TextAreaField("News text", validators=[DataRequired()]) 
    submit = SubmitField("Отправить новость")






@app.route('/social/', methods=['GET', 'POST'])
def login():

    msg = ''
    
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
      
        username = request.form['username']
        password = request.form['password']
     
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = %s', [username])
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


        cursor = conn.cursor()
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
            conn.commit()
            msg = 'Вы успешно зарегестрировались!'

    
    elif request.method == 'POST':
          msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

@app.route('/social/home', methods=['GET', 'POST'])
def home():
    #if 'loggedin' in session:
        cursor = conn.cursor()
        form = NewsForm()
        if form.validate_on_submit():
            news_text = form.news_text.data
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('INSERT INTO news ( author_id, news_text, news_date )   VALUES(%s, %s, %s) ', (session['id'], news_text, timestamp  ),)
            conn.commit()
            cursor.execute('SELECT name, surname FROM accounts WHERE id = %s', (session['id'],))
            account = cursor.fetchone()
            username = account['name'] + " " + account['surname']
            cursor.close()
            return redirect(url_for('home'))
     
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        cursor.execute('SELECT * FROM accounts LEFT JOIN friends  ON accounts.id =  friends.friend_id WHERE friends.account_id =  %s ', (session['id'],))
        friends = cursor.fetchall()
        cursor.execute('SELECT * FROM news WHERE author_id =  %s limit 10', (session['id'],))
        news = cursor.fetchall()
        cursor.close()
        return render_template('home.html', account=account, friends=friends, news=news,  form=form)
    #return redirect(url_for('login'))
    

@app.route('/social/profile')
def profile():
    if 'loggedin' in session:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        cursor.close()
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))

@app.route('/social/displaypeople', methods=['GET'])
def displaypeople():
    #if 'loggedin' in session:
        user_name = request.args.get('name') 
        user_surname = request.args.get('surname') 
        if user_name:
            cursor = conn.cursor()
            user_name_String = user_name + "%" 
            user_surname_String =  user_surname + "%"
            cursor.execute('SELECT id,username, name , surname, email  FROM accounts where name LIKE  %s and surname LIKE %s   ORDER  BY  id ASC LIMIT 50', ([user_name_String],[user_surname_String]))
            account = cursor.fetchall()
            cursor.close()
            return render_template('displaypeople.html', account=account)
        else:    
            cursor = conn.cursor()
            cursor.execute('SELECT id,username, name , surname, email  FROM accounts where id != %s LIMIT 50', [session['id']],)
            account = cursor.fetchall()
            cursor.close() 
            if account:        
                return render_template('displaypeople.html', account=account)
            else:
                return render_template('displaypeople.html')
        return redirect(url_for('login'))


    


@app.route('/social/displayfriend', methods=['GET', 'POST'])
def displayfriend():
    if 'loggedin' in session:
        form = ChatForm()
        cursor = conn.cursor()
        if form.validate_on_submit():
            friend_id = request.args.get('friend_id')
            chat_text = form.chat_text.data
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('INSERT INTO dialogs (  message_from, message_to ,message_text ,message_date )   VALUES(%s, %s, %s, %s) ', (session['id'], friend_id, chat_text, timestamp  ),)
            сonn.commit()
            cursor.close()
            return redirect(url_for('displayfriend'))
        friend_id = request.args.get('friend_id')
        cursor.execute('SELECT * FROM accounts where id = %s',   [friend_id])
        account = cursor.fetchone()
        cursor.execute('SELECT user1.name, user2.name,  message_text, message_date FROM dialogs   \
        left join accounts as user1 on dialogs.message_from  = user1.id \
        left join accounts as user2 on dialogs.message_to  = user2.id \
        where  (dialogs.message_from = %s and dialogs.message_to = %s ) OR (dialogs.message_from = %s and dialogs.message_to = %s ) ;',   (session['id'],friend_id,friend_id,session['id']))
        dialog = cursor.fetchall()
        cursor.close()
        return render_template('displayfriend.html', account=account, dialog=dialog, form=form )
    return redirect(url_for('login'))


@app.route('/social/displayman', methods=['GET', 'POST'])
def displayman():
    if 'loggedin' in session:
        form = AddFriendForm()
        user_id = request.args.get('user_id') 
        cursor = conn.cursor()
        if form.validate_on_submit():
            
            cursor.execute('SELECT *  FROM friends where account_id = %s and friend_id = %s', (session['id'], user_id ))
            friend = cursor.fetchone()
            if friend:
                cursor.close()
                return "Этот человек уже у вас в друзьях!"
            else: 
                cursor.execute('INSERT INTO friends ( account_id, friend_id )   VALUES(%s, %s) ', (session['id'], user_id ),)
                conn.commit()
                cursor.execute('SELECT name, surname FROM accounts where id = %s',  [user_id])
                account = cursor.fetchone()
                flash("Пользователь "+ account['name'] +" "+ account['surname']+" добавлен в друзья", "success")
                cursor.close()
                return redirect(url_for('displaypeople'))

        cursor.execute('SELECT * FROM accounts where id = %s',   [user_id])
        account = cursor.fetchone()
        cursor.close()
        return render_template('displayman.html', account=account, form=form)
    return redirect(url_for('login'))




@app.route('/social/news', methods=['GET'])
def news():
#    if 'loggedin' in session:
    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # cursor.execute('SELECT acc.name  as acc_name, acc.surname as acc_surname, news_text, news_date \
    # from news left join accounts as acc on news.author_id  = acc.id where author_id in \
    # (SELECT friend_id from    friends where account_id = %s)',  (session['id'],))
    # news = cursor.fetchall()
    # cursor.close()
 
    #mysql_slave()
    

    

    #conn = pymysql.connect(**mysql_slave)
    cursor = conn.cursor()
    
    
    cursor.execute('SELECT news_text, news_date, author_name from news limit 10')
    news_stream =  cursor.fetchall()
    cursor.close()

    #conn = pymysql.connect(**mysql_master)
    

    #return render_template('news.html', news=news, news_stream=news_stream)

    return render_template('news.html',  news_stream=news_stream)

    return redirect(url_for('login')) 



@app.route('/social/webs', methods=['GET', 'POST'])
def webs():
    
    cursor = conn.cursor()
    cursor.execute('SELECT news_text, news_date, author_name from news  LIMIT 10')
    news_stream =  cursor.fetchall()
    cursor.close()

    
    return render_template('webs.html',  news_stream=news_stream)
    


if __name__ == "__main__":
    application.run(debug=True,host='0.0.0.0')
