#R5 wraps - это помощник создания декораторов
from functools import wraps;
from flask import current_app, flash, request, redirect, url_for;
#config -нужен для доступа к EXEMPT_METHODS
from flask_login import config, current_user;
from flask_babel import _

newsIndex = "news.index";

def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in config.EXEMPT_METHODS:
            return func(*args, **kwargs);
        elif current_app.config.get('LOGIN_DISABLED'):
            return func(*args, **kwargs);
        elif not current_user.is_authenticated:
            return current_app.login_manager.unauthorized();
        elif not current_user.is_admin:
            flash(_('Эта страница доступна только группе администраторов.'));
            return redirect(url_for(newsIndex));
        return func(*args, **kwargs);
    return decorated_view;
