from my_project.dao import film_dao

class FilmNotFoundException(Exception):
    pass

class FilmExistsException(Exception):
    pass

def create_new_film(db, film_schema):
    existing_film = film_dao.get_film_by_title_year(db, film_schema.title, film_schema.year)
    if existing_film:
        raise FilmExistsException("Exists")
    
    return film_dao.create_film(db, film_schema)

def get_film_by_id(db, film_id):
    db_film = film_dao.get_film(db, film_id)
    if db_film is None:
        raise FilmNotFoundException("Not found")
    return db_film

def get_all_films_service(db, skip, limit):
    return film_dao.get_all_films(db, skip, limit)

def update_existing_film(db, film_id, film_update):
    db_film = get_film_by_id(db, film_id)
    
    return film_dao.update_film(db, db_film, film_update)

def delete_existing_film(db, film_id):
    db_film = get_film_by_id(db, film_id)
    
    film_dao.delete_film(db, db_film)

def get_film_reviews_service(db, film_id):
    db_film = film_dao.get_film_with_reviews(db, film_id)
    if db_film is None:
        raise FilmNotFoundException("Not found")
    return db_film