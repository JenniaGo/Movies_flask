from flask import Flask, render_template, url_for, request, redirect, session
import requests
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = 'YevgenyGoGoGo132'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///localhost:27017/MoviesDB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Movie object
class Movie:
    def __init__(self,id,title,overview,poster,vote_average,vote_count,date_release):
        self.id = id
        self.title = title
        self.overview = overview
        self.poster = 'https://image.tmdb.org/t/p/w500/'+ poster
        self.vote_average = vote_average
        self.vote_count = vote_count
        self.date_release = date_release

# Review object
class Review(db.Model):

    __tablename__ = "reviews"

    id = db.Column(db.Integer,primary_key = True)
    movie_id = db.Column(db.Integer)
    movie_title = db.Column(db.String)
    image_path = db.Column(db.String)
    review_title = db.Column(db.String)
    movie_review = db.Column(db.String)
    user_name = db.Column(db.String)
    posted = db.Column(db.DateTime,default=datetime.utcnow)

    def save_review(review):
        db.session.add(review)
        db.session.commit()

    @classmethod
    def get_reviews(cls,id):
        reviews = Review.query.filter_by(movie_id = id).all()
        return reviews


# tmdb api
api_key = '***API TOKEN PLACE HERE***'
discover_base_url = "https://api.tmdb.org/3/discover/movie/?api_key="+api_key
base_url = "https://api.themoviedb.org/3/movie/{}?api_key={}"


def process_results(movie_list):
    """
    Function  that processes the movie result and transform them to a list of Objects
    Args:
        movie_list: A list of dictionaries that contain movie details
    Returns :
        movie_results: A list of movie objects
    """
    movie_results = []
    for movie_item in movie_list:
        id = movie_item.get('id')
        title = movie_item.get('title')
        overview = movie_item.get('overview')
        poster = movie_item.get('poster_path')
        vote_average = movie_item.get('vote_average')
        vote_count = movie_item.get('vote_count')
        date_release = movie_item.get('release_date')

        if poster:
            movie_object = Movie(id, title, overview, poster, vote_average, vote_count, date_release)
            movie_results.append(movie_object)

    return movie_results

# get movies from categories
def get_movies(category):
    """
    Function that gets the json response to our url request
    """
    get_movies_url = base_url.format(category, api_key)
    get_movies_response = requests.get(get_movies_url).json()

    if get_movies_response['results']:
        movie_results_list = get_movies_response['results']
        movie_results = process_results(movie_results_list)

    return movie_results

# get movie details from movie id
def get_movie(id):
    get_movie_details_url = base_url.format(id, api_key)
    movie_details_response = requests.get(get_movie_details_url).json()

    if movie_details_response:
        id = movie_details_response.get('id')
        title = movie_details_response.get('original_title')
        overview = movie_details_response.get('overview')
        poster = movie_details_response.get('poster_path')
        vote_average = movie_details_response.get('vote_average')
        vote_count = movie_details_response.get('vote_count')
        date_release = movie_details_response.get('release_date')

        movie_object = Movie(id, title, overview, poster, vote_average, vote_count,date_release)

    return movie_object

# Search movie by name
def search_movie(movie_name):

    search_movie_url = 'https://api.themoviedb.org/3/search/movie?api_key={}&query={}'.format(api_key, movie_name)
    search_movie_response = requests.get(search_movie_url).json()

    if search_movie_response['results']:
        search_movie_list = search_movie_response['results']
        search_movie_results = process_results(search_movie_list)
        print(search_movie_results)
        return search_movie_results

@app.route('/')
@app.route('/home')
@app.route('/index')
def index():
    popular_movies = get_movies("popular")
    upcoming_movie = get_movies("upcoming")
    now_showing_movie = get_movies("now_playing")
    title = 'Home - Welcome to The best Movie Review Website Online'

    search_movie = request.args.get('movie_query')
    if search_movie:
        return redirect(url_for('search',movie_name=search_movie))
    else:
        return render_template('index.html',
                                title = title,
                                popular = popular_movies,
                                upcoming = upcoming_movie,
                                now_showing = now_showing_movie)

# Show detail of each movie
@app.route("/movie/<int:id>")
def movie(id):
    movie = get_movie(id)
    title = f'{movie.title}'
    reviews = Review.query.filter_by(movie_id =id).all()
    return render_template("movie.html", id=id, title=title, movie=movie, reviews=reviews)

# Search movie by name
@app.route('/search/<movie_name>')
def search(movie_name):
    '''
    View function to display the search results
    '''
    movie_name_list = movie_name.split(" ")
    movie_name_format = "+".join(movie_name_list)
    searched_movies = search_movie(movie_name_format)
    title = f'search results for {movie_name}'
    return render_template("search.html", title=title, movies=searched_movies)

@app.route('/Poster')
def Poster():
    return render_template("Poster.html")


@app.route('/movie/review/new/<int:id>', methods=['GET', 'POST'])
def new_review(id):
    movie = get_movie(id)

    if request.method == "POST":
        title = request.form['title']
        review = request.form['review']
        user_name = request.form['user_name']
        new_review = Review(movie_id=movie.id, movie_title=movie.title, image_path=movie.poster, review_title=title, movie_review=review, user_name=user_name)
        try:
            new_review.save_review()
            return redirect(url_for('movie'), id=movie.id)
        except Exception as error:
            print(f'Unexpected error: {error}')

    title = f'{movie.title} review'
    return render_template('new_review.html', title=title, movie=movie)


@app.route("/review/<int:id>")
def single_review(id):
    review = Review.query.get_or_404(id)
    return render_template("review.html", review=review)



if __name__ == "__main__":
    app.run(debug=True, port=5007)
