from flask import Blueprint

bp = Blueprint('valided_phones', __name__)

from app.valided_phones import routes