from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from my_project.database import get_db
from my_project.service import procedure_service
from my_project.service.procedure_service import InvalidOperatorException

insert_10_bp = Blueprint('insert_10', __name__, url_prefix='/insert_10')
maths_function_bp = Blueprint('maths', __name__, url_prefix='/maths')
proc_cursor_bp = Blueprint('proc_cursor', __name__, url_prefix='/proc_cursor')

def with_db_session(f):
    def wrapper(*args, **kwargs):
        db = next(get_db())
        try:
            return f(db, *args, **kwargs)
        finally:
            db.close()
    wrapper.__name__ = f.__name__
    return wrapper

@insert_10_bp.route('/', methods=['POST'])
@with_db_session
def insert_10(db: Session):
    try:
        procedure_service.insert_10_service(db)
        
        return jsonify({
            "message": "insert 10 finished",
            "status": "completed"
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Insert 10 Error: {e}"}), 500
    

@maths_function_bp.route('/<operator>', methods=['GET'])
@with_db_session
def maths_function(db: Session, operator: str):
    try:
        result = procedure_service.maths_function_service(db, operator)
        
        if result is None:
            return jsonify({"operation": operator.upper(), "result": None, "message": "empty"}), 404
            
        return jsonify({"operation": operator.upper(), "result": result}), 200
        
    except InvalidOperatorException as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error: {e}"}), 500
    

@proc_cursor_bp.route('/', methods=['POST'])
@with_db_session
def proc_cursor(db: Session):
    try:
        procedure_service.proc_cursor_service(db)
        
        return jsonify({
            "message": "cursor finished",
            "status": "completed"
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"cursor failed: {e}"}), 500