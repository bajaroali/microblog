from flask import render_template, flash, redirect, url_for, request
from urllib.parse import urlsplit
from datetime import datetime, timezone
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm
from app.models import User
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from werkzeug.utils import secure_filename
from uuid import uuid4
from app import flask_uuid
import os


@app.route('/')
@app.route('/index')
@login_required
def index():
  """the index/ home page endpoint"""
  posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
  return render_template("index.html", title='Home Page', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)        
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You been logged out successfully.')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
      uploaded_picture = request.files['profile_picture']
      uploaded_picture_name = secure_filename(uploaded_picture.filename)
      #generate a unique user identifier (uuid)
      random_uuid = str(uuid4())
      #combine the random uuid to the uploaded image name to 
      profile_pic_name = str(random_uuid) + "_" + uploaded_picture_name
      #save uploaded image to images folder
      uploaded_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_pic_name))
      #OR use the  absolute path
      #uploaded_picture.save(os.path.join(os.getcwd(), 'app', 'static', 'images', profile_pic_name))
      user = User(username= (form.username.data).strip(), email=(form.email.data).strip(), about_me = form.about.data, profile_picture = profile_pic_name)
        #profile_picture = request.files['profile_picture']
      user.set_password(form.password.data)
      db.session.add(user)
      db.session.commit()  
      flash('Congratulations "{}", you are now a registered user!'.format((form.username.data).strip()))
      return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    form = EmptyForm()
    user = db.first_or_404(sa.select(User).where(User.username == username))
    return render_template('user.html', user=user, posts=posts, form=form)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)
    
@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f'You are following {username}!')
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You are not following {username}.')
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))
      
# Pass stuff to the Navbar
#@app.context.processor
#def basefilesearchform():
 # form = SearchForm()
 # return dict(form=form)