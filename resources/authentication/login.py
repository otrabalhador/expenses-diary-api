import flask_login
import flask_restful as restful
from flask import request
from flask_login import login_required, logout_user

from database.connection import db_conn
from database.execute import execute_to_scalar
from logger.logger import new
from queries.authentication import SELECT_USER_ID
from returns.bad_request import missing_fields
from returns.internal_server_error import unexpected_error
from utils.validate_body import validate_body

logger = new("Authentication")

REQUIRED_COLUMNS = [
    "email",
    "password"
]

COLUMNS = [
    "email",
    "password"
]

class Login(restful.Resource):
    def __init__(self):
        pass

    @staticmethod
    def post():
        try:
            import login_manager.manager

            conn = db_conn()
            content = validate_body(request.get_json(), REQUIRED_COLUMNS, COLUMNS)
            user_id = execute_to_scalar(conn, SELECT_USER_ID, content)

            conn.close()
            if not isinstance(user_id, type(None)):
                user = login_manager.manager.User(user_id)
                flask_login.login_user(user)

                logger.info("Usuário %s logado no sistema." % user_id)

                return {
                           "message": "Login efetuado com sucesso!"
                       }, 200
            else:
                return {
                           "message": "Informações de email e senha inválidos."
                       }, 401
        except KeyError as error:
            logger.info(error)
            return missing_fields(error.fields)
        except Exception as error:
            logger.error(error)
            return unexpected_error()


class Logout(restful.Resource):
    def __init__(self):
        pass

    @staticmethod
    @login_required
    def post():
        import login_manager.manager
        logout_user()
        return {"message": 'Logged out'}, 200
