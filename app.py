from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from data import Articles
#import ConnectionManager
import sqlite3
import os
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app=Flask(__name__)

#database connection creation
database=os.getcwd()+'\\flaskapp.db'
conn=sqlite3.connect(database, check_same_thread=False)
#cursor=conn.cursor()

@app.route('/Home')
def index():
    return render_template('Home.html')

#contacts
@app.route('/contacts')
def contact():
    return render_template('contact_us.html')

#All articles
data_articles=Articles()
@app.route('/Articles')
def articles():
    return render_template('articles.html', articles=data_articles)

#single article
@app.route('/article/<string:id>/')
def article_sub(id):
    return render_template('article.html', id=id)

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=20)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password',[
    validators.DataRequired(),
    validators.EqualTo('confirm',message='passwords do not match')
    ])
    confirm=PasswordField('Confirm Password')

#New user registration
@app.route('/register',methods=['GET','POST'])
def register():
    form=RegisterForm(request.form)
    if request.method=='POST' and form.validate():
        #id=form.id.data
        name=form.name.data
        email=form.email.data
        username=form.username.data
        password=sha256_crypt.encrypt(str(form.password.data))

        form_data=[name,email,username,password]
        cursor=conn.cursor()
        cursor.execute("insert into users(name,email,username,password,created_time) values(?,?,?,?,datetime('now','localtime'))",form_data)
        conn.commit()

        #cursor.close()
        #conn.close()

        flash('You my friend are now registerd with us', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

#User authentication and login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        #get form fields
        username=request.form['username']
        password_candidate=request.form['password']
        #password=sha256_crypt.decrypt(password_candidate)
        cursor=conn.cursor()
        result=cursor.execute("select * from users where username=? ;",[username]).fetchone()

        if result>0:
            password=result[4]

            #compare passwords
            if sha256_crypt.verify(password_candidate,password):
                #Passed
                session['logged_in']=True
                session['username']=username

                flash('You are now logged in','success')
                return redirect(url_for('dashboard'))
            else:
                error='invalid login'
                return render_template('login.html', error=error)
            #closing cursor
            cursor.close()
        else:
            error='user not found'
            return render_template('login.html', error=error)
    return render_template('login.html')

#check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, please login','danger')
            return redirect(url_for('login'))
    return wrap


#Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have successfully logged out', 'success')
    return redirect(url_for('login'))

#Dashboard for logged in users
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')

if __name__=='__main__':
    app.secret_key='secret123'
    app.run(debug=True)
