import datetime
import os
import gunicorn
import psycopg2
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from classes.forms import *
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, logout_user, LoginManager, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "akldf*(Oalksf"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL1", "sqlite:///static/data/cars.db")

# Form Settings
ckeditor = CKEditor(app)

# Database
db = SQLAlchemy(app)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Date Settings
today = datetime.date.today()
year = today.year


# database models
class Users(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)

    def __repr__(self):
        return {
            "id": self.id,
            "password": self.password,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name
        }


class ForumPost(db.Model):
    __tablename__ = "forumpost"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    created_by = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    replies = db.relationship('Replies', backref='ForumPost', lazy=True)

    def __repr__(self):
        return {
            "id": self.id,
            "title": self.title,
            "created_by": self.created_by,
            "body": self.body,
            "date": self.date,
            "replies": self.replies
        }


class Replies(db.Model):
    __tablename__ = "replies"
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime)
    post_id = db.Column(db.Integer, db.ForeignKey('forumpost.id'))

    def __repr__(self):
        return {
            "id": self.id,
            "created_by": self.created_by,
            "body": self.body,
            "date": self.date,
            "post_id": self.post_id
        }


class Cars(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    vin = db.Column(db.String, nullable=False)
    fname = db.Column(db.String, nullable=False)
    lname = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)

    def __repr__(self):
        return {"id": self.id,
                "year": self.year,
                "vin": self.vin,
                "fname": self.fname,
                "lname": self.lname,
                "email": self.email
                }


db.create_all()
posts = db.session.query(ForumPost).all()


@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html', year=year)


@app.route("/login", methods=["GET", "POST"])
def login():
    login_form = UserForm()
    if request.method == "POST":
        user = Users.query.filter_by(email=login_form.email.data).first()
        if user:
            if check_password_hash(user.password, login_form.password.data):
                flash(f"Welcome {user.first_name}!")
                login_user(user)
                return redirect("/home")
            else:
                flash("Invalid Password")
        else:
            flash("User not found")
    return render_template('login.html', login_form=login_form)


@app.route("/logout", methods=["Get", "Post"])
def logout():
    logout_user()
    flash("You have been logged out!")
    return redirect(url_for('login'))


@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    form = UserForm()
    if request.method == "POST":
        user = Users.query.filter_by(email=form.email.data).first()
        if not user:
            if form.password.data == request.form["conf_pass"]:
                new_user = Users(email=form.email.data,
                                 first_name=form.first_name.data,
                                 last_name=form.last_name.data,
                                 password=generate_password_hash(form.password.data))
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('index'))
            else:
                flash("Passwords do not Match")
                redirect(url_for('sign_up'))
        else:
            flash("Email Already Registered.")
            redirect(url_for('login'))
    return render_template("sign_up.html", form=form)


@app.route('/forum', methods=["GET", "POST"])
def forum():
    global posts
    posts = db.session.query(ForumPost).all()
    form = AddPostForm()

    if request.method == "POST":
        post = ForumPost(
            title=request.form["title"],
            created_by=f"{current_user.first_name} {current_user.last_name}",
            body=request.form["body"],
            date=today
        )
        try:
            db.session.add(post)
            db.session.commit()
        except:
            pass
        posts = db.session.query(ForumPost).all()
        return redirect('forum')

    return render_template('forum.html', year=year, posts=posts, form=form)


@app.route('/forum/<title>/<id>', methods=["GET", "POST"])
def forum_post(id, title):
    form = ReplyPost()
    display_post = db.session.query(ForumPost).get(id)
    return render_template('forum_post.html', form=form, post=display_post, year=year, current_user=current_user)


@app.route('/add-reply', methods=["POST"])
def add_reply():
    if request.method == "POST":
        print(request.form)
        reply = Replies(
            created_by=f"{current_user.first_name} {current_user.last_name} ",
            body=request.form["body"],
            date=today,
            post_id=request.form["post_id"]
        )

        db.session.add(reply)
        db.session.commit()
    return redirect('forum')


@app.route('/gallery')
def gallery():
    return render_template('gallery.html', year=year)


@app.route('/registry')
def registry():
    cars = db.session.query(Cars).all()
    return render_template('registry.html', cars=cars)


@app.route('/add_car', methods=["POST"])
def add_car():
    car = Cars(
        year=int(request.form["year"]),
        vin=request.form["vin"],
        fname=request.form["fname"],
        lname=request.form["lname"],
        email=request.form["email"]
    )
    if request.method == "POST":
        db.session.add(car)
        db.session.commit()
    return redirect('registry')


if __name__ == "__main__":
    app.run(debug=True)
