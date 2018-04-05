from flask import Flask, render_template, request, redirect, session, flash
import md5, re
import os, binascii 
from mysqlconnection import MySQLConnector
app = Flask(__name__)
app.secret_key = "secret_key"
mysql = MySQLConnector(app, 'wall')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def wall_index():
    return render_template('wall_index.html')

@app.route('/register', methods=["POST"])
def register():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = md5.new(request.form['password']).hexdigest()
    password_conf = md5.new(request.form['password_conf']).hexdigest()

    errors = False #boolean. To verify the information
    if len(first_name) == 0:
        flash ('Please submit the name')
        errors = True
    elif first_name!=first_name.isalpha:
        flash ('Name can only contain letters')
        errors = True
    if len(last_name) == 0:
        flash ('Please submit the name')
        errors = True
    elif first_name!=last_name.isalpha:
        flash ('Name can only contain letters')
        errors = True
    if len(email) == 0:
        flash ('Please submit the email')
        errors = True
    elif not EMAIL_REGEX.match(email):
        flash ('Invalid email')
        errors = True
    if len(password) == 0:
        flash ('Please submit the password')
        errors = True
    elif len(password) < 8:
        flash ('Password must have, at least, 8 characters')
        errors = True
    if len(password_conf) == 0:
        flash ('Please confirm the password')
        errors = True
    elif password != password_conf:
        flash ('Passwords must match')
        errors = True
    if errors:
        return redirect('/')
    else:
        query = "SELECT * FROM users WHERE email = :email LIMIT 1" 
        data = { #not quite sure about this one
            'first_name': request.form ['first_name'],
            'last_name': request.form ['last_name'],
            'email': request.form['email'],
            'password': request.form['password']
        }

        users = mysql.query_db(query, data)
        if len(users) >0:
            flash('Use another email. This is already taken')
            return redirect('/')

        query = 'INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW())'
        user_id = mysql.query_db(query,data)
        session['user_id'] = user_id
        session['first_name'] = first_name
        
        return redirect('/the_wall')

@app.route('/login', methods=["POST"])
def login():
    password = md5.new(request.form['password']).hexdigest()
    email = request.form['email']
    
    query = "SELECT * FROM users where users.email = :email AND users.password = :password"
    data = {
        'email': email 
    }
    users = mysql.query_db(query,data)
    if len(users) > 0: #to verify/match that user exists
        user = users[0] 
    # encrypt thingy here. Not quite sure how to
        return redirect('/the_wall')
    else:
        flash('Invalid Email/Password Combination. Please submit if again')
        return redirect('/')

@app.route('/the_wall')
def wall():

    return render_template('wall_itself.html')

#This gave me errors. Not sure what's wrong.
# @app.route('/the_wall')
# def wall():
#     query = "SELECT CONCAT(users.first_name, ' ', users.last_name) AS name, messages.id, messages.message, messages.created_at FROM users JOIN messages ON messages.user_id = users.id;"
#     messages = mysql.query_db(query)

#     query = "SELECT CONCAT(users.first_name, ' ', users.last_name) AS name, comments.comment, comments.message_id, comments.created_at FROM users JOIN comments ON users.id = comments.user_id;"
#     comments = mysql.query_db(query)

#     return render_template('wall_itself.html')
#     # , messages=messages, comments=comments)

@app.route('/messages', methods=["POST"])
def create_message():
    query = "INSERT INTO messages (user_id, message, created_at, updated_at) VALUES (:user_id, :message, NOW(), NOW())"
    data = {
        'user_id': session['user_id'],
        'message': request.form['message_content']
    }
    mysql.query_db(query, data)

    return redirect('/the_wall')

@app.route('/comments', methods=["POST"])
def create_comment():
    query = "INSERT INTO comments (user_id, message_id, comment, created_at, updated_at) VALUES (:user_id, :mess_id, :comment, NOW(), NOW())"
    data = {
        'user_id': session['user_id'],
        'message_id': request.form['message_id'],
        'comment': request.form['comment']
    }
    mysql.query_db(query, data)

    return redirect('/the_wall')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

app.run(debug=True)