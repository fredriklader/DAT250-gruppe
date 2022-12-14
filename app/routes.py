from flask import render_template, flash, redirect, url_for, request, session
from app import app, query_db
from app.forms import IndexForm, PostForm, FriendsForm, ProfileForm, CommentsForm
from datetime import datetime
import os
from flask_uploads import UploadSet, configure_uploads

#Nytt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from functools import wraps
from datetime import timedelta
from config import User


#Session attempt counter deletet after 5 minutes
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)

login = LoginManager(app)
login.login_view="index"

@login.user_loader
def load_user(user_id):
    user = query_db('SELECT * FROM Users WHERE id="{}";'. format(user_id), one=True)
    if user is None:
        return None
    else:
        return User(user_id, user[1])

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = IndexForm()
    #Initiaxlise session counter to 0
    if session.get("count")==None:
        session["count"]=0

    if form.login.is_submitted() and form.login.submit.data:
        user = query_db('SELECT * FROM Users WHERE username="{}";'.format(form.login.username.data), one=True)
        #Denies user with 5 or more login attemps
        if int(session.get("count")) >= 4:
            flash('To many attemps!')
        elif user == None:
            flash('Username or password is incorrect!')
            #if username does not exist add session count +1
            session["count"]=int(session.get("count")) +1

        #checking the password entered with the password in the database
        elif check_password_hash(user['password'], form.login.password.data):
            #logs in user with flask-login
            user2=User(id=user["id"], username=user["username"])
            login_user(user2)
            #storing username in session for url managment
            session["username"] = user['username']
            recaptcha_reg_response = request.form['g-recaptcha-response']
            if len(recaptcha_reg_response)>1:
                return redirect(url_for('stream', username=form.login.username.data))
        else:
            #if password is incorrect add session count +1
            flash('Username or password is incorrect!')
            session["count"]=int(session.get("count")) +1
            return redirect(url_for('index'))

    elif form.register.is_submitted() and form.register.submit.data:
        #Hashing password with salt
        hash_password=generate_password_hash(form.register.password.data, method="sha256", salt_length=8)
        #checking if username already exist
        if query_db('SELECT * FROM Users WHERE username="{}";'.format(form.register.username.data), one=True)!=None:
            flash("Sorry, username already exist!")
        #checking if confirm password and password is equal, and the length of username and password. Adding to database
        elif form.register.password.data==form.register.confirm_password.data and len(form.register.password.data)>=8 and len(form.register.username.data)>=4:
            query_db('INSERT INTO Users (username, first_name, last_name, password) VALUES("{}", "{}", "{}", "{}");'.format(form.register.username.data, form.register.first_name.data,
            form.register.last_name.data, hash_password))  
             
        #Printing if username is to short
        elif len(form.register.username.data)<=4:
            flash('Username must contain at least 4 characters')
        #Printing if username is to long
        elif len(form.register.username.data)>=16:
            flash('Username can only contain up to 15 characters')
        #Printing if first_name is to short
        elif len(form.register.first_name.data)<=2:
            flash('It must contain at least 2 characters')
        #Printing if first_name is to long
        elif len(form.register.first_name.data)>=30:
            flash('It must only contain up to 30 characters')
        #Printing if first_name is to short
        elif len(form.register.last_name.data)<=2:
            flash('It must contain at least 2 characters')
        #Printing if first_name is to long
        elif len(form.register.last_name.data)>=30:
            flash('It must only contain up to 30 characters')
        
        
        #Printing if password is to short
        elif len(form.register.password.data)<8:
            flash('Password must contain at least 8 characters')   
        #Printing if password and confirm password is not equal
        else:
            flash('Sorry, passwords does not match!')
        return redirect(url_for('index'))
    return render_template('index.html', title='Welcome', form=form)



# content stream page
@app.route('/stream/<username>', methods=['GET', 'POST'])
@login_required
def stream(username):
    #redirects to index.html if urls username is not equal to session username. 
    #Session username is only set thrue index.html
    if session.get("username") != username:
        return redirect(url_for('index'))
    #if logged in to account, session count is set back to 0
    session["count"]=0
    form = PostForm()
    user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    if form.validate_on_submit():
        if form.image.data:
            path = os.path.join(app.config['UPLOAD_PATH'], form.image.data.filename)
            form.image.data.save(path) 
        query_db('INSERT INTO Posts (u_id, content, image, creation_time) VALUES({}, "{}", "{}", \'{}\');'.format(user['id'], form.content.data, form.image.data.filename, datetime.now()))
        return redirect(url_for('stream', username=username))
    posts = query_db('SELECT p.*, u.*, (SELECT COUNT(*) FROM Comments WHERE p_id=p.id) AS cc FROM Posts AS p JOIN Users AS u ON u.id=p.u_id WHERE p.u_id IN (SELECT u_id FROM Friends WHERE f_id={0}) OR p.u_id IN (SELECT f_id FROM Friends WHERE u_id={0}) OR p.u_id={0} ORDER BY p.creation_time DESC;'.format(user['id']))
    return render_template('stream.html', title='Stream', username=username, form=form, posts=posts)

# comment page for a given post and user.
@app.route('/comments/<username>/<int:p_id>', methods=['GET', 'POST'])
@login_required
def comments(username, p_id):
    #redirects to index.html if urls username is not equal to session username. 
    #Session username is only set thrue index.html
    if session.get("username") != username:
        return redirect(url_for('index'))
    form = CommentsForm()
    if form.validate_on_submit():
        user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
        query_db('INSERT INTO Comments (p_id, u_id, comment, creation_time) VALUES({}, {}, "{}", \'{}\');'.format(p_id, user['id'], form.comment.data, datetime.now()))

    post = query_db('SELECT * FROM Posts WHERE id={};'.format(p_id), one=True)
    all_comments = query_db('SELECT DISTINCT * FROM Comments AS c JOIN Users AS u ON c.u_id=u.id WHERE c.p_id={} ORDER BY c.creation_time DESC;'.format(p_id))
    return render_template('comments.html', title='Comments', username=username, form=form, post=post, comments=all_comments)    

# page for seeing and adding friends
@app.route('/friends/<username>', methods=['GET', 'POST'])
@login_required
def friends(username):
    #redirects to index.html if urls username is not equal to session username. 
    #Session username is only set thrue index.html
    if session.get("username") != username:
        return redirect(url_for('index'))
    form = FriendsForm()
    user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    if form.validate_on_submit():
        friend = query_db('SELECT * FROM Users WHERE username="{}";'.format(form.username.data), one=True)
        if friend is None:
            flash('User does not exist')
        else:
            query_db('INSERT INTO Friends (u_id, f_id) VALUES({}, {});'.format(user['id'], friend['id']))
    
    all_friends = query_db('SELECT * FROM Friends AS f JOIN Users as u ON f.f_id=u.id WHERE f.u_id={} AND f.f_id!={} ;'.format(user['id'], user['id']))
    return render_template('friends.html', title='Friends', username=username, friends=all_friends, form=form)

# see and edit detailed profile information of a user
@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    #redirects to index.html if urls username is not equal to session username. 
    #Session username is only set thrue index.html
    if session.get("username") != username:
        return redirect(url_for('index'))
    form = ProfileForm()
    if form.validate_on_submit():
        query_db('UPDATE Users SET education="{}", employment="{}", music="{}", movie="{}", nationality="{}", birthday=\'{}\' WHERE username="{}" ;'.format(
            form.education.data, form.employment.data, form.music.data, form.movie.data, form.nationality.data, form.birthday.data, username
        ))
        return redirect(url_for('profile', username=username))
    
    user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    return render_template('profile.html', title='profile', username=username, user=user, form=form)

@app.route('/ShowAbout/<username>', methods=['GET', 'POST'])
@login_required
def ShowAbout(username):
    #redirects to index.html if urls username is not equal to session username. 
    #Session username is only set thrue index.html
    friend=username
    user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    return render_template('ShowAbout.html', title='ShowAbout', friend=friend, user=user, username=session.get("username"))

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    #clear session username and redirects to index.html
    logout_user()
    session["username"]=None
    return redirect(url_for('index'))
