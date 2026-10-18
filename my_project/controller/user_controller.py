from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from sqlalchemy.orm import Session
from my_project.database import get_db
from my_project.service import user_service
from my_project.service.user_service import UserNotFoundException, UserExistsException
from my_project.domain.schemas import UserCreate, UserUpdate, UserResponse, ReviewResponse
from functools import wraps

user_bp = Blueprint('users', __name__, url_prefix='/users')

def with_db_session(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        db = next(get_db())
        try:
            return f(db, *args, **kwargs)
        finally:
            db.close()
    return wrapper

@user_bp.route('/', methods=['POST'])
@with_db_session
def create_user_endpoint(db: Session):
    """
    Create new user
    ---
    tags:
      - Users
    parameters:
      - in: body
        name: body
        required: true
        description: Data for user creation
        schema:
          type: object
          required:
            - nick_name
            - email
            - registration_date
          properties:
            nick_name:
              type: string
              example: "user"
            email:
              type: string
              example: "user@gmail.com"
            registration_date:
              type: string
              format: date
              example: "2026-10-15"
            human_id:
              type: integer
              example: 1
    responses:
      200:
        description: Successfully created
        schema:
          type: object
          properties:
            id:
              type: integer
            nick_name:
              type: string
            email:
              type: string
            registration_date:
              type: string
              format: date
      400:
        description: Validation error
        schema:
          type: object
          properties:
            error:
              type: array
              items:
                type: object
      409:
        description: Already exists
        schema:
          type: object
          properties:
            error:
              type: string
    """
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
    """
    Get users array
    ---
    tags:
      - Users
    responses:
      200:
        description: Users array
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              username:
                type: string
              email:
                type: string
    """
    users = user_service.get_all_users_service(db, 0, 100)
    response_data = [UserResponse.model_validate(f).model_dump() for f in users]
    return jsonify(response_data), 200

@user_bp.route('/<int:user_id>', methods=['GET'])
@with_db_session
def get_user_endpoint(db: Session, user_id: int):
    """
    Get user by ID
    ---
    tags:
      - Users
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: User ID
    responses:
      200:
        description: User details
        schema:
          type: object
          properties:
            id:
              type: integer
            username:
              type: string
            email:
              type: string
      404:
        description: User not found
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        user = user_service.get_user_by_id(db, user_id)
        return jsonify(UserResponse.model_validate(user).model_dump()), 200
    except UserNotFoundException as e:
        return jsonify({"error": str(e)}), 404

@user_bp.route('/<int:user_id>', methods=['PUT'])
@with_db_session
def update_user_endpoint(db: Session, user_id: int):
    """
    Update user by ID
    ---
    tags:
      - Users
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: User ID
      - in: body
        name: body
        required: true
        description: Fields to update (all optional)
        schema:
          type: object
          properties:
            username:
              type: string
              example: "updated_user"
            email:
              type: string
              example: "updatedemail@gmail.com"
    responses:
      200:
        description: User successfully updated
        schema:
          type: object
          properties:
            id:
              type: integer
            username:
              type: string
            email:
              type: string
      400:
        description: Input data validation error
        schema:
          type: object
          properties:
            error:
              type: array
              items:
                type: object
      404:
        description: User not found
        schema:
          type: object
          properties:
            error:
              type: string
    """
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
    """
    Delete user by ID
    ---
    tags:
      - Users
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: User ID
    responses:
      200:
        description: User successfully deleted
        schema:
          type: object
          properties:
            message:
              type: string
              example: "User deleted"
      404:
        description: User not found
        schema:
          type: object
          properties:
            error:
              type: string
    """
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