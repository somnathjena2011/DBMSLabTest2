from flask import render_template, url_for, flash, redirect, session, abort, request
from app import app, mysql, bcrypt
from app.forms import RegistrationForm, LoginForm
from datetime import date

@app.route("/")
@app.route("/home")
def home():
    cursor = mysql.connection.cursor()
    res = cursor.execute("SELECT * FROM room;")
    rooms = cursor.fetchall()
    return render_template('home.html',title='Home',rooms=rooms)

@app.route('/register',methods=['GET','POST'])
def register():
    if 'loggedin' in session:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        cursor = mysql.connection.cursor()
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        try:
            cursor.execute("INSERT INTO user(username,email,password) VALUES('{}','{}','{}')".format(
                form.username.data,form.email.data,hashed_pw
            ))
            mysql.connection.commit()
            cursor.close()
            flash(f'Account created for {form.username.data}. You can login now!')
            return redirect(url_for('login'))
        except:
            flash(f'User exists')
            return redirect(url_for('home'))
    return render_template('register.html',title='Reigster',form=form)

@app.route('/user')
def user():
    cursor = mysql.connection.cursor()
    res = cursor.execute("SELECT * FROM user")
    if res>0:
        users = cursor.fetchall()
        return render_template('users.html',users=users)

@app.route('/login',methods=['GET','POST'])
def login():
    if 'loggedin' in session:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        cursor = mysql.connection.cursor()
        res = cursor.execute("SELECT * FROM user WHERE email='{}'".format(
            form.email.data
        ))

        if res>0:
            user = cursor.fetchone()
            if user and bcrypt.check_password_hash(user[3],form.password.data):
                session['loggedin'] = True
                session['id'] = user[0]
                session['username'] = user[1]
                flash(f'Logged in successfuly')
                return redirect(url_for('home'))
            else:
                flash(f'Cannot login')
                return redirect(url_for('home'))
        else:
            flash(f'Cannot login')
            return redirect(url_for('home'))

    return render_template('login.html',title='Login',form=form)

@app.route('/logout')
def logout():
    if 'loggedin' in session:
        session.pop('loggedin',None)
        session.pop('id',None)
        session.pop('username',None)
        return redirect(url_for('home'))

@app.route('/account')
def account():
    if 'loggedin' in session:
        return render_template('account.html',title='Account')
    else:
        return redirect(url_for('login'))

@app.route('/find/<int:room_id>',methods=['POST'])
def find(room_id):
    details = request.form
    from_date = details['from_date']
    to_date = details['to_date']

    cursor = mysql.connection.cursor()
    res = cursor.execute("SELECT R.room_id, R.room_type, R.charge FROM room R WHERE R.room_id={}\
         AND R.room_id NOT IN (SELECT room_id FROM booking WHERE (to_date>='{}' AND to_date<='{}') OR\
             (from_date>='{}' AND from_date<='{}'))"
             .format(room_id,from_date,to_date,from_date,to_date))
    room = cursor.fetchone()
    isAvailable = False
    if res>0:
        isAvailable=True
    return render_template('room.html',isAvailable=isAvailable,room=room)