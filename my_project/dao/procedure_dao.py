from sqlalchemy import text
from my_project.database import get_db
from sqlalchemy.orm import Session

def insert_10(db):
    sql_call = text("CALL insert_packet_10_()")
    
    try:
        db.execute(sql_call)
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        raise Exception(f"Error: {e}")


def maths_function(db: Session, operator):
    result_value = None
    
    with db.begin():
            connection = db.connection()
            raw_connection = connection.connection 
            
            cursor = raw_connection.cursor() 
            
            try:
                cursor.callproc('call_procedure', [operator])
                
                for result in cursor.stored_results():
                    data = result.fetchone()
                    if data:
                        result_value = data[0]
                        break 
                        
            except Exception as e:
                raise Exception(f"Error: {e}")
            finally:
                cursor.close()
            
            return result_value



def proc_cursor(db):
    sql_call = text("CALL ProcCursor()")
    
    try:
        db.execute(sql_call)
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        raise Exception(f"Cursor Error: {e}")