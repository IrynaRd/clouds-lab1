from my_project.dao import procedure_dao

def insert_10_service(db):
    print("insert 10")
    return procedure_dao.insert_10(db)

operators = ['SUM', 'AVG', 'MAX', 'MIN']

class InvalidOperatorException(Exception):
    pass

def maths_function_service(db, operator: str):
    operator_upper = operator.upper()
    
    if operator_upper not in operators:
        raise InvalidOperatorException(f"{operator} not in {operators}")
        
    return procedure_dao.maths_function(db, operator_upper)


def proc_cursor_service(db):
    print("cursor")
    return procedure_dao.proc_cursor(db)