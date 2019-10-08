from flask import Blueprint

bp = Blueprint('master_schedule', __name__, template_folder='templates')

from app.master_schedule import routes