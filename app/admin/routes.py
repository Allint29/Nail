from flask import render_template
from app.admin import bp
from app.decorators.decorators import admin_required
from flask_babel import _

@bp.route('/')
@admin_required
def admin_index():
    titleVar='Панель админа'
    return render_template('admin/index.html', title=titleVar)