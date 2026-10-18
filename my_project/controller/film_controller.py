from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from sqlalchemy.orm import Session
from my_project.database import get_db
from my_project.service import film_service
from my_project.service.film_service import FilmNotFoundException, FilmExistsException
from my_project.domain.schemas import FilmCreate, FilmUpdate, FilmResponse, ReviewResponse
from functools import wraps

film_bp = Blueprint('films', __name__, url_prefix='/films')

def with_db_session(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        db = next(get_db())
        try:
            return f(db, *args, **kwargs)
        finally:
            db.close()
    return wrapper

@film_bp.route('/', methods=['POST'])
@with_db_session
def create_film_endpoint(db: Session):
    """
    Create a new film
    ---
    tags:
      - Films
    parameters:
      - in: body
        name: body
        required: true
        description: Film details
        schema:
          type: object
          required:
            - title
            - year
            - description
            - budget
          properties:
            title:
              type: string
              example: "Film"
            year:
              type: integer
              example: 2010
            description:
              type: string
              example: "Film about ..."
            budget:
              type: number
              format: double
              example: 16045568789.00
    responses:
      200:
        description: Film successfully created
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            title:
              type: string
              example: "Film"
            year:
              type: integer
              example: 2010
            description:
              type: string
              example: "Film about .."
            budget:
              type: number
              format: double
              example: 16045568789.00
      400:
        description: Input data validation error
        schema:
          type: object
          properties:
            error:
              type: array
              items:
                type: object
      409:
        description: Film already exists
        schema:
          type: object
          properties:
            error:
              type: string
              example: "exists"
    """
    try:
        film_schema = FilmCreate.model_validate(request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    
    try:
        new_film = film_service.create_new_film(db, film_schema)
        return jsonify(FilmResponse.model_validate(new_film).model_dump()), 201
    except FilmExistsException as error:
        return jsonify({"error": str(error)}), 409

@film_bp.route('/', methods=['GET'])
@with_db_session
def get_films_endpoint(db: Session):
    """
    Get films array
    ---
    tags:
      - Films
    responses:
      200:
        description: Films array
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              title:
                type: string
              year:
                type: integer
              description:
                type: string
              budget:
                type: number
    """
    films = film_service.get_all_films_service(db, 0, 100)
    response_data = [FilmResponse.model_validate(f).model_dump() for f in films]
    return jsonify(response_data), 200

@film_bp.route('/<int:film_id>', methods=['GET'])
@with_db_session
def get_film_endpoint(db: Session, film_id: int):
    """
    Get a movie by ID
    ---
    tags:
      - Films
    parameters:
      - in: path
        name: film_id
        type: integer
        required: true
        description: Film ID
    responses:
      200:
        description: Film details
        schema:
          type: object
          properties:
            id:
              type: integer
            title:
              type: string
            year:
              type: integer
            description:
              type: string
            budget:
              type: number
      404:
        description: Film not found
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        film = film_service.get_film_by_id(db, film_id)
        return jsonify(FilmResponse.model_validate(film).model_dump()), 200
    except FilmNotFoundException as e:
        return jsonify({"error": str(e)}), 404

@film_bp.route('/<int:film_id>', methods=['PUT'])
@with_db_session
def update_film_endpoint(db: Session, film_id: int):
    """
    Update film data by ID
    ---
    tags:
      - Films
    parameters:
      - in: path
        name: film_id
        type: integer
        required: true
        description: Film ID
      - in: body
        name: body
        required: true
        description: Fields to update (all optional)
        schema:
          type: object
          properties:
            title:
              type: string
              example: "Updated title"
            year:
              type: integer
              example: 2023
            description:
              type: string
              example: "Updated description"
            budget:
              type: number
              example: 200000000.00
    responses:
      200:
        description: Film successfully updated
        schema:
          type: object
          properties:
            id:
              type: integer
            title:
              type: string
            year:
              type: integer
            description:
              type: string
            budget:
              type: number
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
        description: Film not found
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        film_update_schema = FilmUpdate.model_validate(request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
        
    try:
        updated_film = film_service.update_existing_film(db, film_id, film_update_schema)
        return jsonify(FilmResponse.model_validate(updated_film).model_dump()), 200
    except FilmNotFoundException as e:
        return jsonify({"error": str(e)}), 404

@film_bp.route('/<int:film_id>', methods=['DELETE'])
@with_db_session
def delete_film_endpoint(db: Session, film_id: int):
    """
    Delete film by ID
    ---
    tags:
      - Films
    parameters:
      - in: path
        name: film_id
        type: integer
        required: true
        description: Film ID
    responses:
      200:
        description: Film successfully deleted
        schema:
          type: object
          properties:
            message:
              type: string
              example: "film deleted"
      404:
        description: Film not found
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        film_service.delete_existing_film(db, film_id)
        return jsonify({"message": "film deleted"}), 200
    except FilmNotFoundException as e:
        return jsonify({"error": str(e)}), 404

@film_bp.route('/<int:film_id>/reviews', methods=['GET'])
@with_db_session
def get_film_reviews_endpoint(db: Session, film_id: int):
    
    """всі рецензії для одного фільму"""
    
    try:
        film_with_reviews = film_service.get_film_reviews_service(db, film_id)
        reviews_data = [
            ReviewResponse.model_validate(review).model_dump() 
            for review in film_with_reviews.reviews
        ]
        return jsonify(reviews_data), 200
    
    except FilmNotFoundException as e:
        return jsonify({"error": str(e)}), 404