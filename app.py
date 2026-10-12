from flask import Flask
from my_project.controller.film_controller import film_bp
from my_project.controller.user_controller import user_bp
from my_project.controller.review_controller import review_bp
from my_project.controller.procedure_controller import insert_10_bp, maths_function_bp, proc_cursor_bp
from my_project.database import engine, Base

app = Flask(__name__)
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

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)