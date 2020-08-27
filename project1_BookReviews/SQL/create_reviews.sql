CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rating_score INTEGER NOT NULL,
    content VARCHAR,
    review_time TIMESTAMP NOT NULL
);
