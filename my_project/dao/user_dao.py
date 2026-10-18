from sqlalchemy import select, text
from sqlalchemy.orm import joinedload
from my_project.domain.models import User

def get_user(db, user_id):
    query = select(User).where(User.id == user_id)
    return db.scalars(query).first()

def get_user_by_nick_name(db, nick_name):
    query = select(User).where(User.nick_name == nick_name)
    return db.scalars(query).first()

def get_all_users(db, skip = 0, limit = 100):
    query = select(User).offset(skip).limit(limit)
    return db.scalars(query).all()

def create_user(db, user_schema):
    user_data = user_schema.model_dump(exclude={'human_id'})
    db_user = User(**user_data)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db, db_user, user_update):
    update_data = user_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
        
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db, db_user):
    db.delete(db_user)
    db.commit()


def get_user_with_reviews(db, user_id):
    query = select(User).options(joinedload(User.reviews)).where(User.id == user_id)
    
    return db.scalars(query).first()


def craete_user_sp(db, user_data):
    nick_name = user_data['nick_name']
    email = user_data['email']
    registration_date = user_data['registration_date'] 
    human_id = user_data['human_id']

    sql_call = text("""CALL insert_with_params(:name, :email, :register, :h_id)""")
    
    try:
        db.execute(
            sql_call, 
            {
                'name': nick_name, 
                'email': email, 
                'register': registration_date, 
                'h_id': human_id
            }
        )
        db.commit()

        return get_user_by_nick_name(db, nick_name)
        
    except Exception as e:
        db.rollback()
        raise Exception(f"Error insert_with_params: {e}")