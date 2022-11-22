DROP TABLE IF EXISTS reviews;

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
  	movie_id INTEGER,
  	movie_title TEXT NOT NULL,
 	review_title TEXT NOT NULL,
    image_path TEXT NOT NULL,
  	movie_review TEXT NOT NULL,
    user_name TEXT NOT NULL,
  	posted TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
