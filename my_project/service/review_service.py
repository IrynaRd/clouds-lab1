from my_project.dao import review_dao, film_dao, user_dao

class ReviewNotFoundException(Exception):
    pass

class ReviewExistsException(Exception):
    pass

class FilmNotFoundException(Exception):
    pass

class UserNotFoundException(Exception):
    pass


def create_new_review(db, review_schema):
    if film_dao.get_film(db, review_schema.film_id) is None:
        raise FilmNotFoundException("Film Not found")
        
    if user_dao.get_user(db, review_schema.user_id) is None:
        raise UserNotFoundException("Not found")

    existing_review = review_dao.get_review(db, review_schema.film_id, review_schema.user_id)
    if existing_review:
        raise ReviewExistsException("Exists")
    
    return review_dao.create_review(db, review_schema)

def get_review_by_ids(db, film_id, user_id):
    db_review = review_dao.get_review(db, film_id, user_id)
    if db_review is None:
        raise ReviewNotFoundException("Review Not found")
    return db_review

def update_existing_review(db, film_id, user_id, review_update):
    db_review = get_review_by_ids(db, film_id, user_id)
    
    return review_dao.update_review(db, db_review, review_update)

def delete_existing_review(db, film_id, user_id):
    db_review = get_review_by_ids(db, film_id, user_id)
    
    review_dao.delete_review(db, db_review)


def get_reviews_for_film_service(db, film_id):
    if film_dao.get_film(db, film_id) is None:
        raise FilmNotFoundException("Film Not found")
        
    return review_dao.get_reviews_for_film(db, film_id)

def get_reviews_by_user_service(db, user_id):
    if user_dao.get_user(db, user_id) is None:
        raise UserNotFoundException("User not found")
        
    return review_dao.get_reviews_by_user(db, user_id)

def get_films_with_reviews_service(db, skip: int = 0, limit: int = 10):

    return review_dao.get_films_with_reviews(db, skip=skip, limit=limit)

def create_review_sp(db, review_schema):
    review_data = review_schema.model_dump()
    return review_dao.create_review_sp(db, review_data)