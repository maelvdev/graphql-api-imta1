import json

def write_movies(movies):
    with open("./data/movies.json", "w") as f:
        json.dump({"movies": movies}, f)

def load_movies():
    with open("./data/movies.json", "r") as f:
        return json.load(f)["movies"]

def load_actors():
    with open("./data/actors.json", "r") as f:
        return json.load(f)["actors"]