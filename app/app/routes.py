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
         AND R.room_id NOT IN (SELECT room_id FROM booking WHERE ((to_date>='{}' AND to_date<='{}') OR\
             (from_date>='{}' AND from_date<='{}')) AND booked=TRUE)"
             .format(room_id,from_date,to_date,from_date,to_date))
    isAvailable = False
    if res>0:
        room = cursor.fetchone()
        isAvailable=True
        return render_template('room.html',isAvailable=isAvailable,room=room,from_date=from_date,to_date=to_date)
    else:
        res = cursor.execute("SELECT R.room_id, R.room_type, R.charge FROM room R WHERE R.room_id={}"\
             .format(room_id))
        room = cursor.fetchone()
        isAvailable = False
        return render_template('room.html',isAvailable=isAvailable,room=room,from_date=from_date,to_date=to_date)

@app.route('/book/<int:room_id>',methods=['POST'])
def book(room_id):
    if 'loggedin' not in session:
        flash('Login first')
        return redirect(url_for('login'))
    else:
        details = request.form
        room_id = int(details['room_id'])
        room_type = details['room_type']
        charge = float(details['charge'])
        from_date = details['from_date']
        to_date = details['to_date']
        room = {
            'room_id': room_id,
            'room_type': room_type,
            'charge': charge,
            'from_date': from_date,
            'to_date': to_date
        }
        return render_template('book.html',room=room)

@app.route('/finish/<int:room_id>',methods=['POST'])
def finish(room_id):
    if 'loggedin' not in session:
        flash('Login first')
        return redirect(url_for('login'))
    else:
        details = request.form
        room_id = int(details['room_id'])
        room_type = details['room_type']
        charge = float(details['charge'])
        from_date = details['from_date']
        to_date = details['to_date']
        people = int(details['people'])
        description = details['description']

        print("user_id="+str(session['id']))
        print("room_id="+str(room_id))
        print("room_type="+room_type)
        print("from_date="+from_date)
        print("to_date="+to_date)

        cursor = mysql.connection.cursor()
        res = cursor.execute("SELECT R.room_id, R.room_type, R.charge FROM room R WHERE R.room_id={}\
            AND R.room_id NOT IN (SELECT room_id FROM booking WHERE ((to_date>='{}' AND to_date<='{}') OR\
                (from_date>='{}' AND from_date<='{}')) AND booked=TRUE)"
                .format(room_id,from_date,to_date,from_date,to_date))
        isAvailable = False
        if res>0:
            isAvailable=True
        if isAvailable:
            cursor.execute("INSERT INTO booking(user_id,room_id,room_type,from_date,to_date,booked,people,description) VALUES({},{},'{}','{}','{}',TRUE,{},'{}')".format(
                session['id'],room_id,room_type,str(from_date),str(to_date),people,description))
            mysql.connection.commit()
            cursor.close()
            flash(f'Booking succesful!')
            return redirect(url_for('home'))
        else:
            cursor.execute("INSERT INTO booking(user_id,room_id,room_type,from_date,to_date,booked,pending)\
                 VALUES({},{},'{}','{}','{}',FALSE,TRUE)".format(int(session['id']),room_id,room_type,from_date,to_date))
            mysql.connection.commit()
            cursor.close()
            flash(f'Booking pending!')
            return redirect(url_for('home'))

@app.route('/bookings')
def bookings():
    if 'loggedin' not in session:
        flash('Login first')
        return redirect(url_for('login'))
    else:
        cursor = mysql.connection.cursor()
        res = cursor.execute("SELECT * FROM booking WHERE user_id={}".format(session['id']))
        books = cursor.fetchall()
        return render_template('books.html',books=books)

@app.route('/cancel/<int:booking_id>',methods=['POST'])
def cancel(booking_id):
    if 'loggedin' not in session:
        flashh('Login first')
        return redirect(url_for('login'))
    else:
        cursor = mysql.connection.cursor()
        res = cursor.execute("SELECT room_id FROM booking WHERE booking_id={}".format(booking_id))
        room_id = cursor.fetchone()[0]
        cursor.close()
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM booking WHERE booking_id={}".format(booking_id))
        mysql.connection.commit()
        cursor.close()
        cursor = mysql.connection.cursor()
        res = cursor.execute("SELECT booking_id FROM booking WHERE room_id={} AND booked=FALSE AND pending=TRUE ORDER BY from_date ASC".format(room_id))
        if res>0:
            bookingId = cursor.fetchone()[0]
            print("booking_id="+str(bookingId))
            cursor.execute("UPDATE booking SET booked=TRUE, pending=FALSE WHERE booking_id={}".format(int(bookingId)))
            mysql.connection.commit()
        cursor.close()
        return redirect(url_for('home'))