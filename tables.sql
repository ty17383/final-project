DROP TABLE users;
DROP TABLE books;
DROP TABLE reviews;

CREATE TABLE users (user_id INTEGER, username TEXT NOT NULL, hash TEXT NOT NULL, PRIMARY KEY(user_id));

CREATE TABLE books(book_id INTEGER, title TEXT, author TEXT, series TEXT, pages INTEGER, PRIMARY KEY(book_id));

CREATE TABLE reviews(book_id INTEGER, user_id year, done BOOL, year_finished INTEGER, month_finished INTEGER, rating INTEGER, PRIMARY KEY(book_id, user_id));