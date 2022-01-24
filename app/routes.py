import secrets
import os
from flask import render_template, url_for, flash, redirect, abort, request, make_response
from app import app, db, models, bcrypt
from app.forms import PostForm, LoginForm, RegistrationForm, UpdateAccountForm
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy import desc, exc
from PIL import Image

####################
#### Home Route ####
####################

@app.route('/')
@app.route('/home')
def home():
    posts = models.Post.query.order_by(desc(models.Post.date_posted))
    
    try:
        return render_template('home.html', title='Home', posts=posts)
    except:
        return abort(404)

###############################
#### Example Cookie Routes ####
###############################

@app.route('/cookie')
def cookie():
    '''
    I can set cookies like this!
    '''
    res = make_response(redirect(url_for('home')))
    res.set_cookie('cookie', value='I am a delicious cookie!')
    flash('I just set a cookie!', category='success')

    return res

@app.route('/get-cookie')
def get_cookie():
    '''
    I can get a cookie like this!
    '''
    cookie_data = request.cookies.get('cookie')
    flash(f'My cookie contained {cookie_data}', category='success')
    return redirect(url_for('home'))

####################
#### About Route ####
####################
@app.route('/about')
def about():
    '''Renders the about page.
    '''
    try:
        return render_template('about.html', title='About')
    except:
        return abort(404)

#####################
#### Login Route ####
#####################
@app.route('/login', methods=['GET', 'POST'])
def login():
    '''Renders the login page if current_user is not authenticated.
    Otherwise redirects to the home route.
    '''

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)

            flash(f'Login successful for user: {user.username}', category='success')
            if (user.admin == True):
                try:
                    return redirect(url_for('userlist'))
                except:
                    return abort(404)
            else:
                try:
                    return redirect(url_for('account'))
                except:
                    return abort(404)
        else:
            flash(f'Login unsuccessful. Please verify your email and password.', 'danger')
    try:
        return render_template('login.html', title='Login', form=form)
    except:
        return abort(404)

################################
#### Register Account Route ####
################################
@app.route('/register', methods=['GET', 'POST'])
def register():
    '''Renders the register account page if current_user is not authenticated.
    Otherwise redirects to the home route.
    '''

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        try:
            user = models.User(
                username=form.username.data,
                email=form.email.data, 
                password_hash=hashed_pass)
            db.session.add(user)
            db.session.commit()
            # The user has registered an account
            # Log the user in automatically for a single session
            login_user(user, remember=False)
            flash(f'Account created for {form.username.data}!', category='success')
            return redirect(url_for('account'))
        except exc.SQLAlchemyError as e:
            flash(f'Error with database. SQL error: {e}', category='danger')
            return redirect(url_for('home'))
    try:
        return render_template('register.html', title='Register', form=form)
    except:
        return abort(404)

######################
#### Logout Route ####
######################
@app.route('/logout')
def logout():
    '''Logs the current_user out and redirects to the home route.
    '''
    logout_user()
    try:
        return redirect(url_for('home'))
    except:
        return abort(404)

################################
#### Admin List Users Route ####
################################
@app.route('/userlist')
@login_required
def userlist():
    '''Renders the userlist page.
    Endpoint is only available if the current_user is logged in, authenticated and an admin account.
    '''

    if current_user.is_authenticated and current_user.admin:
        users = models.User.query.all()
        try:
            return render_template('userlist.html', title="User List", users=users)
        except:
            return abort(404)
    try:
        return redirect(url_for('home'))
    except:
        return abort(404)

#########################
#### View Post Route ####
#########################
@app.route("/post/<int:post_id>")
def post(post_id):
    '''Renders the post page for the post with the requested post_id.
    '''

    try:
        post = models.Post.query.get_or_404(post_id)
        return render_template('post.html', title=post.title, post=post)
    except exc.SQLAlchemyError as e:
        flash(f'Error with database. SQL error: {e}', category='danger')
        return redirect(url_for('home'))

###########################
#### Create Post Route ####
###########################
@app.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():
    '''Renders the create post page.
    Endpoint is only available if logged in.
    '''

    form = PostForm()
    if form.validate_on_submit():
        try:
            post = models.Post(
                user_id=current_user.id,
                title=form.post_title.data,
                content=form.post_body.data
            )
            db.session.add(post)
            db.session.commit()

            flash(f'Post {post.title} created successfully!', category='success')
            return redirect(url_for('home'))
        except exc.SQLAlchemyError as e:
            flash(f'Error with database. SQL error: {e}', category='danger')
            return redirect(url_for('home'))
    try:
        return render_template('createpost.html', title='Create Post', form=form)
    except:
        return abort(404)

###########################
#### Update Post Route ####
###########################
@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    try:
        post = models.Post.query.get_or_404(post_id)
        if post.user_id != current_user.id:
            abort(403)
        try:
            form = PostForm()
            if form.validate_on_submit():
                post.title = form.post_title.data
                post.content = form.post_body.data
                db.session.commit()
                flash(f'Post with id {post.id} successfully updated!', 'success')
                return redirect(url_for('post', post_id=post.id))
            elif request.method == 'GET':
                form.post_title.data = post.title
                form.post_body.data = post.content
            return render_template('editpost.html', title='Edit Post', form=form)
        except exc.SQLAlchemyError as e:
            flash(f'Error with database. SQL error: {e}', category='danger')
            return redirect(url_for('home'))
        except:
            return abort(404)
    except exc.SQLAlchemyError as e:
            flash(f'Error with database. SQL error: {e}', category='danger')
            return redirect(url_for('home'))

###########################
#### Delete Post Route ####
###########################
@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    '''Deletes the post with the requested post_id.
    Endpoint is only available if logged in.
    '''

    try:
        post = models.Post.query.get_or_404(post_id)
        if post.user_id != current_user.id:
            abort(403)
        try:
            db.session.delete(post)
            db.session.commit()
            flash(f'Post {post.id} has been deleted.', category='success')
            return redirect(url_for('home'))
        except exc.SQLAlchemyError as e:
            flash(f'Error with database. SQL error: {e}', category='danger')
            return redirect(url_for('home'))
        except:
            return abort(404)
    except exc.SQLAlchemyError as e:
            flash(f'Error with database. SQL error: {e}', category='danger')
            return redirect(url_for('home'))

###############################
#### Picture Upload Helper ####
###############################
def upload_picture(picture):
    '''Upload a picture
    Get a random sequence of characters first and then append the file extension to it.
    This is to ensure we don't have filename conflicts when multiple users upload image files.
    '''
    hex = secrets.token_hex(8)
    _, file_ext = os.path.split(picture.filename)
    picture_filename = hex + file_ext
    picture_path = os.path.join(app.root_path, 'static/profile_images', picture_filename)
    picture_size = (150, 150)
    image = Image.open(picture)
    image.thumbnail(picture_size)

    image.save(picture_path)

    return picture_filename

############################
#### User Account Route ####
############################
@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    '''Renders the account information page.
    Endpoint is only available if logged in.
    '''

    try:
        form = UpdateAccountForm()
        if form.validate_on_submit():
            
            if form.profile_picture.data:
                profile_picture = upload_picture(form.profile_picture.data)
                current_user.profile_image = profile_picture

            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash(f'Account was succesfully updated.', 'success')
            return redirect(url_for('account'))
        elif request.method == 'GET':
            form.username.data = current_user.username
            form.email.data = current_user.email
        profile_image = url_for('static', filename=f'profile_images/{current_user.profile_image}')
        return render_template('account.html', title="Account", 
                                form=form, profile_image=profile_image)
    except:
        return abort(404)