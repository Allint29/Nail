from flask import Blueprint

bp = Blueprint('admin_my', __name__, template_folder='templates')

from app.admin_my import routes