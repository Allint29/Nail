from flask import Blueprint

bp = Blueprint('welcome', __name__, template_folder='templates')

from app.welcome import routes