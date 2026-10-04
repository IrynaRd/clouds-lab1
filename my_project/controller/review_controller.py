from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from sqlalchemy.orm import Session
from my_project.database import get_db
from my_project.service import review_service
from my_project.service.review_service import (
    ReviewNotFoundException, 
    ReviewExistsException,
    FilmNotFoundException,
    UserNotFoundException
)

from my_project.domain.schemas import ReviewCreate, ReviewUpdate, ReviewResponse, ReviewCreateSP

from my_project.domain.schemas import FilmWithReviewsResponse



review_bp = Blueprint('reviews', __name__, url_prefix='/reviews')

def with_db_session(f):
    def wrapper(*args, **kwargs):
        db = next(get_db())
        try:
            return f(db, *args, **kwargs)
        finally:
            db.close()
    wrapper.__name__ = f.__name__
    return wrapper

@review_bp.route('/', methods=['POST'])
@with_db_session
def create_review_endpoint(db: Session):
    try:
        review_schema = ReviewCreate.model_validate(request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    
    try:
        new_review = review_service.create_new_review(db, review_schema)
        return jsonify(ReviewResponse.model_validate(new_review).model_dump()), 201
    except (FilmNotFoundException, UserNotFoundException) as e:
        return jsonify({"error": str(e)}), 404
    except ReviewExistsException as e:
        return jsonify({"error": str(e)}), 409


@review_bp.route('/film/<int:film_id>/user/<int:user_id>', methods=['GET'])
@with_db_session
def get_review_endpoint(db: Session, film_id: int, user_id: int):
    try:
        review = review_service.get_review_by_ids(db, film_id, user_id)
        return jsonify(ReviewResponse.model_validate(review).model_dump()), 200
    except ReviewNotFoundException as e:
        return jsonify({"error": str(e)}), 404

@review_bp.route('/film/<int:film_id>/user/<int:user_id>', methods=['PUT'])
@with_db_session
def update_review_endpoint(db: Session, film_id: int, user_id: int):

    try:
        review_update_schema = ReviewUpdate.model_validate(request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
        
    try:
        updated_review = review_service.update_existing_review(db, film_id, user_id, review_update_schema)
        return jsonify(ReviewResponse.model_validate(updated_review).model_dump()), 200
    except ReviewNotFoundException as e:
        return jsonify({"error": str(e)}), 404

@review_bp.route('/film/<int:film_id>/user/<int:user_id>', methods=['DELETE'])
@with_db_session
def delete_review_endpoint(db: Session, film_id: int, user_id: int):

    try:
        review_service.delete_existing_review(db, film_id, user_id)
        return jsonify({"message": "Review deleted"}), 200
    except ReviewNotFoundException as e:
        return jsonify({"error": str(e)}), 404


@review_bp.route('/film/<int:film_id>', methods=['GET'])
@with_db_session
def get_reviews_for_film_endpoint(db: Session, film_id: int):
    
    try:
        reviews = review_service.get_reviews_for_film_service(db, film_id)
        response_data = [ReviewResponse.model_validate(r).model_dump() for r in reviews]
        return jsonify(response_data), 200
    except FilmNotFoundException as e:
        return jsonify({"error": str(e)}), 404

@review_bp.route('/user/<int:user_id>', methods=['GET'])
@with_db_session
def get_reviews_by_user_endpoint(db: Session, user_id: int):
    
    try:
        reviews = review_service.get_reviews_by_user_service(db, user_id)
        response_data = [ReviewResponse.model_validate(r).model_dump() for r in reviews]
        return jsonify(response_data), 200
    except UserNotFoundException as e:
        return jsonify({"error": str(e)}), 404
    


@review_bp.route('/films_with_reviews', methods=['GET'])
@with_db_session
def get_films_with_reviews_endpoint(db: Session):
    try:
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 10))
    except ValueError:
        return jsonify({"error": "Invalid 'skip' or 'limit' parameter. Must be integers."}), 400
    
    films = review_service.get_films_with_reviews_service(db, skip, limit)
    
    try:
        response_data = [FilmWithReviewsResponse.model_validate(f).model_dump() for f in films]
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"error": "Failed to serialize response data", "details": str(e)}), 500
    

@review_bp.route('/params', methods=['POST'])
@with_db_session
def create_review_endpoint_ps(db: Session):
    try:
        review_schema = ReviewCreateSP.model_validate(request.json) 
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    
    try:
        new_review_status = review_service.create_review_sp(db, review_schema) 

        if new_review_status is True:
            return jsonify({"message": "Review created successfully"}), 201
        
        return jsonify({"message": "ReviewSP completed"}), 200

    except ReviewExistsException as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500