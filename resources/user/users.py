import flask_restful as restful
from flask import request
from psycopg2._psycopg import AsIs

from database.connection import db_conn
from database.execute import execute_to_json, execute_to_scalar, execute
from logger.logger import new
from queries.user import SELECT_USERS, COUNT_USERS, INSERT_USER, SELECT_USER, UPDATE_USER, DELETE_USER
from returns import status_ok
from returns.bad_request import missing_fields, invalid_fields
from returns.internal_server_error import unexpected_error
from utils.validate_body import validate_body, validate_update_columns

logger = new("User")

COLUMNS = [
    "first_name",
    "last_name",
    "email",
    "password"
]

REQUIRED_COLUMNS = [
    "first_name",
    "last_name",
    "email",
    "password"
]

UPDATEABLE_COLUMNS = [
    "first_name",
    "last_name",
    "email",
    "password"
]


class Users(restful.Resource):
    def __init__(self):
        pass

    @staticmethod
    def get():
        try:
            conn = db_conn()
            response = dict()

            # TODO: get user_id to send to query
            response['content'] = execute_to_json(conn, SELECT_USERS)
            response['total'] = execute_to_scalar(conn, COUNT_USERS)

            conn.close()
            return response, 200
        except Exception as error:
            logger.error(error)
            return unexpected_error()

    @staticmethod
    def post():
        try:
            content = validate_body(request.get_json(), REQUIRED_COLUMNS, COLUMNS)
            logger.info("Request Body: {content}".format(content=content))

            conn = db_conn()
            execute(conn, INSERT_USER, content)
            conn.close()

            return status_ok.inserted()
        except KeyError as error:
            logger.info(error)
            return missing_fields(error.fields)
        except Exception as error:
            logger.info(error)
            return unexpected_error()


class User(restful.Resource):
    def __init__(self):
        pass

    @staticmethod
    def get(id=None):
        try:
            conn = db_conn()
            response = dict()

            response['content'] = execute_to_json(conn, SELECT_USER, (id,))

            conn.close()
            return response, 200
        except Exception as error:
            logger.error(error)
            return unexpected_error()

    @staticmethod
    def patch(id=None):
        try:
            content = validate_update_columns(request.get_json(), UPDATEABLE_COLUMNS)
            logger.info("Request Body: {content}".format(content=content))

            conn = db_conn()

            for key, value in content.items():
                arguments = (AsIs(key), value, id)
                execute(conn, UPDATE_USER, arguments)
            conn.close()

            return status_ok.modified()
        except KeyError as error:
            logger.info(error)
            return invalid_fields(error.fields)
        except Exception as error:
            logger.info(error)
            return unexpected_error()

    @staticmethod
    def delete(id=None):
        try:

            conn = db_conn()
            execute(conn, DELETE_USER, (id,))
            conn.close()

            return status_ok.deactivated()
        except Exception as error:
            logger.info(error)
            return unexpected_error()