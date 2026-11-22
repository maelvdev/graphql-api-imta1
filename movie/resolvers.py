from graphql import GraphQLError
from utils import write_movies, load_actors, load_movies

# QUERIES

def movie_with_id(_, info, _id):
    movies = load_movies()
    for movie in movies:
        if movie["id"] == _id:
            return movie
    return None

def all_movies(_, info):
    return load_movies()

def movie_with_title(_, info, _title):
    movies = load_movies()
    for movie in movies:
        if movie["title"] == _title:
            return movie
    return None

# MUTATIONS

def update_movie_rate(_, info, _id, _rate):
    movies = load_movies()
    for movie in movies:
        if movie["id"] == _id:
            movie["rating"] = _rate
            write_movies(movies)
            return movie
    raise GraphQLError(f"movie {_id} not found")

def delete_movie(_, info, _id):
    movies = load_movies()
    for movie in movies:
        if movie["id"] == _id:
            movies.remove(movie)
            write_movies(movies)
            return movie
    raise GraphQLError(f"movie {_id} not found")

def add_movie(_, info, _id, _title, _rate, _director):
    movies = load_movies()
    
    for movie in movies:
        if movie['id'] == _id:
            raise GraphQLError(f"movie with {_id} already exists")

    new_movie = {
        "id": _id,
        "title": _title,
        "rating": _rate,
        "director": _director
    }
    movies.append(new_movie)
    
    write_movies(movies)
    return new_movie

def resolve_actors_in_movie(movie, info):
    actors = load_actors()
    result = [actor for actor in actors if movie['id'] in actor['films']]
    return result