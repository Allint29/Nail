from flask import render_template
from app import db
from app.errors import bp
from sqlalchemy.exc import InvalidRequestError

@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    try:
        db.session.rollback()
        return render_template('errors/500.html'), 500
    except InvalidRequestError as invalid_request:
        print('My Error: ', invalid_request)
        return render_template('errors/500.html'), 500
