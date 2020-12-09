import os
import calendar

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from helpers import apology, login_required
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///books.db")

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/', methods=["GET"])
@login_required
def index():
    # search db for all books that have been read
    q1 = db.execute(
        "SELECT COUNT(reviews.book_id), SUM(books.pages), AVG(rating) FROM reviews INNER JOIN books ON reviews.book_id=books.book_id WHERE user_id = ? AND done = 1", session["user_id"])
    to_read = db.execute("SELECT COUNT(book_id) FROM reviews WHERE user_id = ? AND done = 0", session["user_id"])

    fields = {
        "book_count": q1[0]["COUNT(reviews.book_id)"],
        "page_count": q1[0]["SUM(books.pages)"],
        "rating": q1[0]["AVG(rating)"],
        "to_read": to_read[0]["COUNT(book_id)"]
    }

    for k, v in fields.items():
        if v == None:
            fields[k] = 0
    fields["rating"] = round(fields["rating"], 1)

    # render template with the books that have been read
    return render_template("index.html", fields=fields)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please enter a username")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please enter a Password")
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Login failed please enter ")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            flash("Please enter a username")
            return render_template("register.html")

        # Ensure password was submitted
        elif not password:
            flash("Please enter a password")
            return render_template("register.html")

        # # password validation 1 - makes sure it is at least 8 characters
        if len(password) < 8:
            flash("password must be at least 8 characters")
            return render_template("register.html")

        # Ensure password was submitted
        elif not confirmation or password != confirmation:
            flash("passwords do not match")
            return render_template("register.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) != 0:
            flash("username already exists")
            return render_template("register.html")

        # generate the id of the user
        count = db.execute("SELECT MAX(user_id) FROM users")

        if count[0]['MAX(user_id)'] == None:
            user_id = 1;
        else:
            user_id = 1 + count[0]['MAX(user_id)']
        # create the new user
        db.execute("INSERT INTO users (user_id, username, hash) VALUES (?, ?, ?)", user_id, username, generate_password_hash(password))

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure title was submitted
        if not request.form.get("title"):
            flash("Title is a required field")
            return render_template("add_book.html")

        # Ensure author was submitted
        elif not request.form.get("author"):
            flash("Author is a required field")
            return render_template("add_book.html")

        # Ensure page count was submitted
        elif not request.form.get("author"):
            flash("Page Count is a required field")
            return render_template("add_book.html")
            # Ensure page count was submitted

        # set series name to none if none is provided
        if not request.form.get("series"):
            series = "none"
        else:
            series = request.form.get("series")

        # set series name to none if none is provided
        book_done = False
        if request.form.get("finished"):
            book_done = True

        # Query database for book
        book_id = db.execute("SELECT book_id FROM books WHERE title= ? AND author = ?",
                             request.form.get("title"), request.form.get("author"))

        # Make sure book does not already exist
        if len(book_id) < 1:
            # generate the id of the user
            count = db.execute("SELECT MAX(book_id) FROM books")

            if count[0]['MAX(book_id)'] == None:
                book_id = 0;
            else:
                book_id = 1 + count[0]['MAX(book_id)']

            db.execute("INSERT INTO books (book_id, title, author, series, pages) VALUES ( ?, ?, ?, ?, ?)", book_id, request.form.get("title"),
                       request.form.get("author"), series, request.form.get("pages"))
        else:
            book_id = book_id[0]['book_id']

        db.execute("INSERT OR IGNORE INTO reviews (book_id, user_id, done) VALUES ( ?, ?, ?)",
                   book_id, session["user_id"], book_done)

        session['title'] = request.form.get("title")
        session['author'] = request.form.get("author")

        # Redirect user to home page
        if book_done:
            flash("Book added successfully")
            return redirect("/review")
        else:
            flash("Book added successfully")
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("add_book.html")


@app.route("/review-seperate", methods=["GET", "POST"])
@login_required
def review_seperate():

   # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure title was submitted
        if not request.form.get("title"):
            flash("Title is a required field 2")
            return render_template("review-seperate.html")

        # Ensure author was submitted
        elif not request.form.get("author"):
            flash("Author is a required field")
            return render_template("review-seperate.html")

        # Ensure year finished was submitted
        if not request.form.get("year_finished"):
            flash("Year Finished is a required field")
            return render_template("review-seperate.html")

        # Ensure month finished was submitted
        elif not request.form.get("month_finished"):
            flash("Month Finished is a required field")
            return render_template("review-seperate.html")

        # Ensure rating was submitted
        elif not request.form.get("author"):
            flash("Book Rating is a required field")
            return render_template("review-seperate.html")

        # Query database for book_id
        book_id = db.execute("SELECT book_id FROM books WHERE title = ? AND author = ?",
                             request.form.get("title"), request.form.get("author"))

        # Make sure that the book exists
        if len(book_id) < 1:
            flash("This book needs to be added before being reviewed")
            return render_template("add_book.html")
        else:
            book_id = book_id[0]['book_id']

        db.execute("DELETE FROM reviews WHERE book_id = ? AND user_id = ?", book_id, session["user_id"])
        db.execute("INSERT INTO reviews (book_id, user_id, done, year_finished, month_finished, rating) VALUES ( ?, ?, ?, ?, ?, ?)", book_id, session["user_id"], True,
                   request.form.get("year_finished"), request.form.get("month_finished"), request.form.get("rating"))

        # Redirect user to home page
        flash("Review added successfully")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("review-seperate.html")


@app.route("/review", methods=["GET", "POST"])
@login_required
def review():

   # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure title was submitted
        if not session["title"]:
            flash("Title is a required field")
            return render_template("review-seperate.html")

        # Ensure author was submitted
        elif not session["author"]:
            flash("Author is a required field")
            return render_template("review-seperate.html")

        # Ensure year finished was submitted
        if not request.form.get("year_finished"):
            flash("Year Finished is a required field")
            return render_template("review.html")

        # Ensure month finished was submitted
        elif not request.form.get("month_finished"):
            flash("Month Finished is a required field")
            return render_template("review.html")
        # Ensure rating was submitted
        elif not request.form.get("rating"):
            flash("Book Rating is a required field")
            return render_template("review.html")

        # Query database for book_id
        book_id = db.execute("SELECT book_id FROM books WHERE title = ? AND author = ?", session["title"], session["author"])
        print(request.form.get("title"))
        print(request.form.get("author"))
        print(book_id)
        # Make sure that the book exists
        if len(book_id) < 0:
            flash("This book needs to be added before being reviewed")
            return render_template("add_book.html")
        else:
            book_id = book_id[0]['book_id']

        db.execute("DELETE FROM reviews WHERE book_id = ? AND user_id = ?", book_id, session["user_id"])
        db.execute("INSERT INTO reviews (book_id, user_id, done, year_finished, month_finished, rating) VALUES ( ?, ?, ?, ?, ?, ?)", book_id, session["user_id"], True,
                   request.form.get("year_finished"), request.form.get("month_finished"), request.form.get("rating"))

        # Redirect user to home page

        flash("Review added successfully")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("review.html")


@app.route("/view", methods=["GET"])
@login_required
def view():

    # search db for all books that have been read
    books = db.execute(
        "SELECT * FROM reviews INNER JOIN books ON reviews.book_id=books.book_id WHERE user_id = ? AND done = 1 ORDER BY year_finished DESC, month_finished DESC", session["user_id"])

    for k in range(len(books)):
        books[k]["month_finished"] = calendar.month_name[books[k]["month_finished"]]

    # render template with the books that have been read
    return render_template("view_books.html", books=books)


@app.route("/view_title", methods=["GET"])
@login_required
def viewTitle():

    # search db for all books that have been read
    books = db.execute(
        "SELECT * FROM reviews INNER JOIN books ON reviews.book_id=books.book_id WHERE user_id = ? AND done = 1 ORDER BY title", session["user_id"])

    for k in range(len(books)):
        books[k]["month_finished"] = calendar.month_name[books[k]["month_finished"]]

    # render template with the books that have been read
    return render_template("view_books.html", books=books)


@app.route("/view_author", methods=["GET"])
@login_required
def viewAuthor():

    # search db for all books that have been read
    books = db.execute(
        "SELECT * FROM reviews INNER JOIN books ON reviews.book_id=books.book_id WHERE user_id = ? AND done = 1 ORDER BY author", session["user_id"])

    for k in range(len(books)):
        books[k]["month_finished"] = calendar.month_name[books[k]["month_finished"]]

    # render template with the books that have been read
    return render_template("view_books.html", books=books)


@app.route("/view_series", methods=["GET"])
@login_required
def viewSeries():

    # search db for all books that have been read
    books = db.execute(
        "SELECT * FROM reviews INNER JOIN books ON reviews.book_id=books.book_id WHERE user_id = ? AND done = 1 AND series != 'none' ORDER BY series", session["user_id"])

    for k in range(len(books)):
        books[k]["month_finished"] = calendar.month_name[books[k]["month_finished"]]

    # render template with the books that have been read
    return render_template("view_books.html", books=books)


@app.route("/view_rating", methods=["GET"])
@login_required
def viewRating():

    # search db for all books that have been read
    books = db.execute(
        "SELECT * FROM reviews INNER JOIN books ON reviews.book_id=books.book_id WHERE user_id = ? AND done = 1 ORDER BY rating DESC", session["user_id"])

    for k in range(len(books)):
        books[k]["month_finished"] = calendar.month_name[books[k]["month_finished"]]

    # render template with the books that have been read
    return render_template("view_books.html", books=books)


@app.route("/to", methods=["GET", "POST"])
@login_required
def to():

    # search db for all books that have been read
    books = db.execute(
        "SELECT * FROM reviews INNER JOIN books ON reviews.book_id=books.book_id WHERE user_id = ? AND done = 0", session["user_id"])

    # render template with the books that have been read
    return render_template("to_read.html", books=books)


@app.route("/to_title", methods=["GET", "POST"])
@login_required
def toTitle():

    # search db for all books that have been read
    books = db.execute(
        "SELECT * FROM reviews INNER JOIN books ON reviews.book_id=books.book_id WHERE user_id = ? AND done = 0 ORDER BY title", session["user_id"])

    # render template with the books that have been read
    return render_template("to_read.html", books=books)


@app.route("/to_author", methods=["GET", "POST"])
@login_required
def toAuthor():

    # search db for all books that have been read
    books = db.execute(
        "SELECT * FROM reviews INNER JOIN books ON reviews.book_id=books.book_id WHERE user_id = ? AND done = 0 ORDER BY author", session["user_id"])

    # render template with the books that have been read
    return render_template("to_read.html", books=books)


@app.route("/to_series", methods=["GET", "POST"])
@login_required
def toSeries():

    # search db for all books that have been read
    books = db.execute(
        "SELECT * FROM reviews INNER JOIN books ON reviews.book_id=books.book_id WHERE user_id = ? AND done = 0 AND series != 'none' ORDER BY series'", session["user_id"])

    # render template with the books that have been read
    return render_template("to_read.html", books=books)
