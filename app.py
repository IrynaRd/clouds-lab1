from flask import Flask, jsonify, request
from my_project.controller.film_controller import film_bp
from my_project.controller.user_controller import user_bp
from my_project.controller.review_controller import review_bp
from my_project.controller.procedure_controller import insert_10_bp, maths_function_bp, proc_cursor_bp
from my_project.database import engine, Base, get_db
from flasgger import Swagger
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
import os
from my_project.domain.models import User

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]
app.config["APP_PASSWORD"] = os.environ["APP_PASSWORD"]
jwt = JWTManager(app)
swagger = Swagger(app)
Base.metadata.create_all(bind=engine)

app.register_blueprint(film_bp)
app.register_blueprint(user_bp)
app.register_blueprint(review_bp)
app.register_blueprint(insert_10_bp)
app.register_blueprint(maths_function_bp)
app.register_blueprint(proc_cursor_bp)

@app.route('/')
def start():
    return "started test"

@app.route('/login', methods=['POST'])
def login():
    """
    User login and JWT generation
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        description: User credentials
        schema:
          type: object
          required:
            - nick_name
            - password
          properties:
            nick_name:
              type: string
              example: "user"
            password:
              type: string
              example: "password"
    responses:
      200:
        description: Successful login
        schema:
          type: object
          properties:
            access_token:
              type: string
      401:
        description: Invalid password
      404:
        description: User not found
    """
    data = request.get_json()
    nick_name = data.get('nick_name')
    password = data.get('password')

    if password != app.config["APP_PASSWORD"]:
        return jsonify({"msg": "Invalid password"}), 401

    db = next(get_db())
    try:
        user = db.query(User).filter(User.nick_name == nick_name).first()
        
        if not user:
            return jsonify({"msg": "User not found"}), 404

        access_token = create_access_token(identity=user.nick_name)
        return jsonify(access_token=access_token), 200
    finally:
        db.close()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)