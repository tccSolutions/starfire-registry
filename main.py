import datetime
import os
import gunicorn
import psycopg2
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from classes.forms import *
from flask_ckeditor import CKEditor

app = Flask(__name__)
ckeditor = CKEditor(app)
app.config["SECRET_KEY"] = "akldf*(Oalksf"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///static/data/cars.db")

db = SQLAlchemy(app)

today = datetime.date.today()
year = today.year


class ForumPost(db.Model):
    __tablename__ = 'forumpost'
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
    __tablename__ = 'cars'
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


@app.route('/forum', methods=["GET", "POST"])
def forum():
    global posts
    posts = db.session.query(ForumPost).all()
    form = AddPostForm()
    if request.method == "POST":
        post = ForumPost(
            title=request.form["title"],
            created_by=request.form["created_by"],
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
    return render_template('forum_post.html', form=form, post=display_post, year=year)


@app.route('/add-reply', methods=["POST"])
def add_reply():
    if request.method == "POST":
        print(request.form)
        reply = Replies(
            created_by=request.form["created_by"],
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
