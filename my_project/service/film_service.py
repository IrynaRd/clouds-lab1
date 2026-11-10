from my_project.dao import film_dao
from my_project.domain.schemas import FilmResponse
from my_project.cache import cache_get, cache_set, cache_delete

class FilmNotFoundException(Exception):
    pass

class FilmExistsException(Exception):
    pass

def create_new_film(db, film_schema):
    existing_film = film_dao.get_film_by_title_year(db, film_schema.title, film_schema.year)
    if existing_film:
        raise FilmExistsException("Exists")

    new_film = film_dao.create_film(db, film_schema)
    cache_delete("films:all")

    return new_film

def get_film_by_id(db, film_id):
    cache_key = f"films:id:{film_id}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    db_film = film_dao.get_film(db, film_id)
    if db_film is None:
        raise FilmNotFoundException("Not found")
        
    film_data = FilmResponse.model_validate(db_film).model_dump()
    cache_set(cache_key, film_data)

    return film_data

def get_all_films_service(db, skip, limit):
    cache_key = "films:all"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    films = film_dao.get_all_films(db, skip, limit)

    films_data = [FilmResponse.model_validate(f).model_dump() for f in films]
    cache_set(cache_key, films_data)

    return films_data

def update_existing_film(db, film_id, film_update):
    db_film = film_dao.get_film(db, film_id)
    if db_film is None:
        raise FilmNotFoundException("Not found")

    updated = film_dao.update_film(db, db_film, film_update)

    cache_delete("films:all")
    cache_delete(f"films:id:{film_id}")

    return updated

def delete_existing_film(db, film_id):
    db_film = film_dao.get_film(db, film_id)
    if db_film is None:
        raise FilmNotFoundException("Not found")

    film_dao.delete_film(db, db_film)

    cache_delete("films:all")
    cache_delete(f"films:id:{film_id}")

def get_film_reviews_service(db, film_id):
    db_film = film_dao.get_film_with_reviews(db, film_id)
    if db_film is None:
        raise FilmNotFoundException("Not found")
    return db_film