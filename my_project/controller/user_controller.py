from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from sqlalchemy.orm import Session
from my_project.database import get_db
from my_project.service import user_service
from my_project.service.user_service import UserNotFoundException, UserExistsException
from my_project.domain.schemas import UserCreate, UserUpdate, UserResponse, ReviewResponse

user_bp = Blueprint('users', __name__, url_prefix='/users')

def with_db_session(f):
    def wrapper(*args, **kwargs):
        db = next(get_db())
        try:
            return f(db, *args, **kwargs)
        finally:
            db.close()
    wrapper.__name__ = f.__name__
    return wrapper

@user_bp.route('/', methods=['POST'])
@with_db_session
def create_user_endpoint(db: Session):
    try:
        user_schema = UserCreate.model_validate(request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    
    try:
        new_user = user_service.create_new_user(db, user_schema)
        return jsonify(UserResponse.model_validate(new_user).model_dump()), 201
    except UserExistsException as e:
        return jsonify({"error": str(e)}), 409

@user_bp.route('/', methods=['GET'])
@with_db_session
def get_users_endpoint(db: Session):
    users = user_service.get_all_users_service(db, 0, 100)
    response_data = [UserResponse.model_validate(f).model_dump() for f in users]
    return jsonify(response_data), 200

@user_bp.route('/<int:user_id>', methods=['GET'])
@with_db_session
def get_user_endpoint(db: Session, user_id: int):
    try:
        user = user_service.get_user_by_id(db, user_id)
        return jsonify(UserResponse.model_validate(user).model_dump()), 200
    except UserNotFoundException as e:
        return jsonify({"error": str(e)}), 404

@user_bp.route('/<int:user_id>', methods=['PUT'])
@with_db_session
def update_user_endpoint(db: Session, user_id: int):
    try:
        user_update_schema = UserUpdate.model_validate(request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
        
    try:
        updated_user = user_service.update_existing_user(db, user_id, user_update_schema)
        return jsonify(UserResponse.model_validate(updated_user).model_dump()), 200
    except UserNotFoundException as e:
        return jsonify({"error": str(e)}), 400

@user_bp.route('/<int:user_id>', methods=['DELETE'])
@with_db_session
def delete_user_endpoint(db: Session, user_id: int):
    try:
        user_service.delete_existing_user(db, user_id)
        return jsonify({"message": "User deleted"}), 200
    except UserNotFoundException as e:
        return jsonify({"error": str(e)}), 404


@user_bp.route('/<int:user_id>/reviews', methods=['GET'])
@with_db_session
def get_user_reviews_endpoint(db: Session, user_id: int):
    """всі рецензії для одного фільму"""
    try:
        user_with_reviews = user_service.get_user_reviews_service(db, user_id)
        reviews_data = [
            ReviewResponse.model_validate(review).model_dump() 
            for review in user_with_reviews.reviews
        ]
        return jsonify(reviews_data), 200
    except UserNotFoundException as e:
        return jsonify({"error": str(e)}), 404
    

@user_bp.route('/params', methods=['POST'])
@with_db_session
def create_user_endpoint_ps(db: Session):
    try:
        user_schema = UserCreate.model_validate(request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    
    try:
        new_user = user_service.create_user_sp(db, user_schema) 
        return jsonify(UserResponse.model_validate(new_user).model_dump()), 201
    except UserExistsException as e:
        return jsonify({"error": str(e)}), 409