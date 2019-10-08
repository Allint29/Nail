from flask import Blueprint

bp = Blueprint('my_work', __name__, template_folder='templates')

from app.my_work import routes