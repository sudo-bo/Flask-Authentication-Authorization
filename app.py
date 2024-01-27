from flask import Flask, request, redirect, render_template, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import User, connect_db, db
from forms import UserLoginForm, UserRegisterForm, UserLogoutForm
# from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///auth_test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.debug = False # can change when needed

app.config['SECRET_KEY'] = 'development key'  # Needed for Flask sessions and debug toolbar
toolbar = DebugToolbarExtension(app)

connect_db(app)
with app.app_context():
    db.create_all()

@app.route("/")
def root():
    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def register_user():
    if session.get('user_id') is None: # if user is logged in, bypass the registration form
        form = UserRegisterForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            email = form.email.data
            first_name = form.first_name.data
            last_name = form.last_name.data

            new_user = User.register(username, password, email, first_name, last_name)

            db.session.add(new_user)
            db.session.commit()

            session['user_id'] = new_user.username
            flash('Registration successful! You can now log in.', 'success')
            return redirect(f'/users/{session["user_id"]}')
        else:
            return render_template('register.html', form=form, value ="register")
    else:
        return redirect(f'/users/{session["user_id"]}')

@app.route("/login", methods=["GET", "POST"])
def login_user():
    if session.get('user_id') is None: # if user is logged in, bypass the login form
        form = UserLoginForm() 
        if form.validate_on_submit():
            user = User.authenticate(form.username.data, form.password.data)
            if user:
                session['user_id'] = user.username
                return redirect(f'/users/{session["user_id"]}')
            else:
                flash('Invalid username or password', 'danger')
                return render_template('register.html', form=form, value ="login")
        else:
            return render_template('register.html', form=form, value ="login")
    else:
        return redirect(f'/users/{session["user_id"]}')


@app.route("/users/<username>", methods=["GET"])
def show_info(username):
    if session.get('user_id') is not None:
        if session.get('user_id') == username:
            user = User.find_user(username=session['user_id'])
            return render_template('secret-info.html', user=user)
        else:
            flash('You are not that user.', 'danger')
            return redirect(f'/users/{session["user_id"]}')
    else:
        flash('Please login or make an account first.', 'danger')
        return redirect('/register')
    
@app.route("/logout", methods = ['GET', 'POST'])
def logout():
    if session.get('user_id') is not None:
        form = UserLogoutForm()
        if form.validate_on_submit():
            logout = form.verify_logout.data
            if logout:
                session.pop('user_id', None) 
                return redirect("/")
            else:
                return redirect(f'/users/{session["user_id"]}')
        else:
            return render_template('/logout.html', form=form)
        
    else: 
        flash('Please login or make an account first.', 'danger')
        return redirect('/register')

