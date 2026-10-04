from sqlalchemy import select, text
from sqlalchemy.orm import selectinload
from my_project.domain.models import Review, Film, User

def create_review(db, review_schema):
    review_data = review_schema.model_dump()
    db_review = Review(**review_data)
    
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def get_review(db, film_id, user_id):
    query = select(Review).where(Review.film_id == film_id,Review.user_id == user_id)
    
    return db.scalars(query).first()

def update_review(db, db_review, review_update):
    update_data = review_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_review, key, value)
        
    db.commit()
    db.refresh(db_review)
    return db_review

def delete_review(db, db_review):
    db.delete(db_review)
    db.commit()


def get_reviews_for_film(db, film_id, skip = 0, limit = 100):
    query = select(Review).where(Review.film_id == film_id).offset(skip).limit(limit)
    
    return db.scalars(query).all()

def get_reviews_by_user(db, user_id, skip = 0, limit = 100):
    query = select(Review).where(Review.user_id == user_id ).offset(skip).limit(limit)
        
    return db.scalars(query).all()


def get_films_with_reviews(db, skip: int = 0, limit: int = 10):
    query = (
        select(Film)
        .options(
            selectinload(Film.reviews)
            .selectinload(Review.user) 
        )
        .order_by(Film.id)
        .offset(skip)
        .limit(limit)
    )
    
    return db.scalars(query).all()

def create_review_sp(db, review_data):
    title = review_data['title']
    nick_name = review_data['nick_name']
    review_text = review_data['review_text'] 
    review_date = review_data['review_date']

    sql_call = text("""CALL insert_M_to_M(:title, :nick_name, :review_text, :review_date)""")
    
    try:
        db.execute(
            sql_call, 
            {
                'title': title, 
                'nick_name': nick_name, 
                'review_text': review_text, 
                'review_date': review_date
            }
        )
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        raise Exception(f"error insert_with_params: {e}")

