from my_project.dao import user_dao

class UserNotFoundException(Exception):
    pass

class UserExistsException(Exception):
    pass

def create_new_user(db, user_schema):
    existing_user = user_dao.get_user_by_nick_name(db, user_schema.nick_name)
    if existing_user:
        raise UserExistsException("User exists")
    
    return user_dao.create_user(db, user_schema)

def get_user_by_id(db, user_id):
    db_user = user_dao.get_user(db, user_id)
    if db_user is None:
        raise UserNotFoundException("User not found")
    return db_user

def get_all_users_service(db, skip, limit):
    return user_dao.get_all_users(db, skip, limit)

def update_existing_user(db, user_id, user_update):
    db_user = get_user_by_id(db, user_id)
    
    return user_dao.update_user(db, db_user, user_update)

def delete_existing_user(db, user_id):
    db_user = get_user_by_id(db, user_id)
    user_dao.delete_user(db, db_user)

def get_user_reviews_service(db, user_id):
    db_user = user_dao.get_user_with_reviews(db, user_id)
    if db_user is None:
        raise UserNotFoundException("Film Not found") 
    return db_user


def create_user_sp(db, user_schema):
    existing_user = user_dao.get_user_by_nick_name(db, user_schema.nick_name)
    if existing_user:
        raise UserExistsException("User exists")
    
    user_data = user_schema.model_dump()
    
    try:
        return user_dao.craete_user_sp(db, user_data)
        
    except Exception as e:
        raise Exception(f"error sp: {e}")