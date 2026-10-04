from sqlalchemy import select
from sqlalchemy.orm import joinedload
from my_project.domain.models import Film


def get_film(db, film_id):
    query = select(Film).where(Film.id == film_id)
    return db.scalars(query).first()

def get_film_by_title_year(db, title, year):
    query = select(Film).where(Film.title == title, Film.year == year)
    
    return db.scalars(query).first()

def get_all_films(db, skip = 0, limit = 100):
    query = select(Film).offset(skip).limit(limit)
    return db.scalars(query).all()

def get_film_with_reviews(db, film_id):
    query = select(Film).options(joinedload(Film.reviews)).where(Film.id == film_id)
    
    return db.scalars(query).first()

def create_film(db, film_schema):
    film_data = film_schema.model_dump()
    db_film = Film(**film_data)
    
    db.add(db_film)
    db.commit()
    db.refresh(db_film)
    return db_film

def update_film(db, db_film, film_update):
    update_data = film_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_film, key, value)
        
    db.commit()
    db.refresh(db_film)
    return db_film

def delete_film(db, db_film):
    db.delete(db_film)
    db.commit()