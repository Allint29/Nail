from flask import render_template
from app.master_schedule import bp
from app.decorators.decorators import admin_required
from flask_babel import _

@bp.route('/')
@admin_required
def index():
    titleVar='Расписание'
    return render_template('master_schedule/index.html', title=titleVar)