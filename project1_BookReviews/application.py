import os
import requests
from flask import Flask, render_template, request, session, flash, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.sql import func
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import IntegrityError
import psycopg2
from types import *
from classes import *

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    if session.get('username', None):
        form = SearchQuery(request.form)
        return render_template("index.html", form=form)
    else:
        return redirect(url_for('login'))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        user_record = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchall()
        if len(user_record) == 0:
            flash(f'Cannot find an account with that username!', 'error')
            return redirect(url_for('login'))
        else:
            input_pwd = request.form.get("pwd")
            if not input_pwd == user_record[0].password_hash:
                flash(f'Password is not correct!', 'error')
                return redirect(url_for('login'))
            else:
                session["username"] = username
                return redirect(url_for('index'))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session["username"] = None
    print(session["username"])
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('username', None):
        return redirect(url_for('index'))
    else:
        form = RegistrationForm(request.form)
        if request.method == 'POST' and form.validate():
            user = User(form.username.data,
                        form.password.data)
            try:
                db.execute(
                    "INSERT INTO users (username, password_hash) VALUES (:username, :password_hash)",
                    {"username": user.username, "password_hash": user.hashed_pwd})
            except IntegrityError as e:
                flash(f'Your username is taken!', 'error')
                return redirect(url_for('register'))
            db.commit()
            flash(u'Thanks for registering. Please log in to access the Library', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', form=form)


@app.route('/search', methods=["POST"])
def search():
    if request.method == "POST":
        query = ''.join(('%', str(request.form.get('query')), '%'))
        if request.form.get('query'):
            isbn_results = db.execute("SELECT * FROM books WHERE isbn LIKE :query", {"query": query}).fetchall()
            title_results = db.execute("SELECT * FROM books WHERE title LIKE :query", {"query": query}).fetchall()
            author_results = db.execute("SELECT * FROM books WHERE author LIKE :query", {"query": query}).fetchall()
            if len(isbn_results) == 0 and len(title_results) == 0 and len(author_results) == 0:
                flash(u'Your query had no results')
                return redirect(url_for('index'))
            else:
                return render_template('search_results.html', query=query,
                                       isbn_results=isbn_results, title_results=title_results,
                                       author_results=author_results)


@app.route('/search_results/<type>/<query>', methods=["GET"])
def search_results(type, query):
    allowed_type = ['isbn', 'title', 'author']
    if type in allowed_type:
        results = db.execute("SELECT * FROM books WHERE " + type + " LIKE :query", {"query": query}).fetchall()
        if len(results) == 0:
            flash(u'Your query had no results')
            return redirect(url_for('index'))
        return render_template('search_results.html', results=results)
    else:
        flash(u'Your query is not allowed')
        return redirect(url_for('index'))


@app.route('/book/<int:id>', methods=["GET"])
def book(id):
    book = db.execute("SELECT * FROM books WHERE id = :book_id", {"book_id": id}).fetchall()
    if len(book) == 0:
        flash(u'Something went wrong. Please try searching again')
        return redirect(url_for('index'))
    else:
        res = requests.get("https://www.goodreads.com/book/review_counts.json",
                           params={"key": "tMQmRxsfTxZmHY0P5jCNg", "isbns": book[0].isbn})
        goodreads_data = {}
        goodreads_data['average_rating'] = res.json()['books'][0]['average_rating']
        goodreads_data['work_ratings_count'] = res.json()['books'][0]['work_ratings_count']
        username = session.get('username', None)
        reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": id}).fetchall()
        can_review = db.execute("SELECT * FROM reviews WHERE book_id = :book_id AND username = :username",
                                {"book_id": id, "username": username}).rowcount == 0
        return render_template('book.html', book=book[0], reviews=reviews, can_review=can_review,
                               goodreads_data=goodreads_data)


@app.route('/submit_review/<int:book_id>/<username>', methods=["POST"])
def submit_review(book_id, username):
    can_review = db.execute("SELECT * FROM reviews WHERE book_id = :book_id AND username = :username",
                            {"book_id": book_id, "username": username}).rowcount == 0
    if can_review:
        content = request.form.get('review_content')
        rating_score = request.form.get('rating')
        db.execute(
            "INSERT INTO reviews (book_id, username, rating_score, content, review_time) VALUES (:book_id, :username, :rating_score, :content, statement_timestamp())",
            {"book_id": book_id, "username": username, "rating_score": rating_score, "content": content})
        db.commit()
    return redirect(url_for('book', id=book_id))


@app.route("/api/<isbn>")
def book_api(isbn):
    """Return details about a book."""
    # Make sure book exists.
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
    if len(book) == 0:
        return jsonify({"error": "Could not find book"}), 404

    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": "tMQmRxsfTxZmHY0P5jCNg", "isbns": book[0].isbn})
    goodreads_data = {}
    goodreads_data['reviews_count'] = float(res.json()['books'][0]['reviews_count'])
    goodreads_data['average_rating'] = float(res.json()['books'][0]['average_rating'])
    goodreads_data['work_ratings_count'] = float(res.json()['books'][0]['work_ratings_count'])

    # get count reviews & sum rating_score
    site_data = db.execute(
        "SELECT COUNT(id) as reviews_count, COALESCE(SUM(rating_score), 0) as sum_rating FROM reviews WHERE book_id = :book_id",
        {"book_id": book[0].id}).fetchall()[0]

    # return book data.
    return jsonify({
        "title": book[0].title,
        "author": book[0].author,
        "year": book[0].year,
        "isbn": book[0].isbn,
        "review_count": goodreads_data['reviews_count'] + site_data.reviews_count,
        "average_score": ((goodreads_data['average_rating'] * goodreads_data[
            'work_ratings_count']) + site_data.sum_rating) / (
                                 goodreads_data['work_ratings_count'] + site_data.reviews_count)
    })
