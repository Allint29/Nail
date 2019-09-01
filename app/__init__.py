# -*- coding: utf-8 -*-
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, _, lazy_gettext as _l
import os
from config import Config
from elasticsearch import Elasticsearch


db = SQLAlchemy()
migrate = Migrate()
loginF = LoginManager()
loginF.login_view = 'auth.login'
loginF.login_message = _l('Пожалуйста, авторизируйтесь, чтобы открыть эту страницу.')
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()
babel = Babel()


#применяю файл конфигурации к объекту app_web
#


def create_app(config_class=Config):
    app_web = Flask(__name__)
    app_web.config.from_object(config_class)

    db.init_app(app_web)
    migrate.init_app(app_web, db)
    loginF.init_app(app_web)
    mail.init_app(app_web)
    bootstrap.init_app(app_web)
    moment.init_app(app_web)
    babel.init_app(app_web)

    from app.errors import bp as errors_bp
    app_web.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app_web.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app_web.register_blueprint(main_bp)

    app_web.elasticsearch = Elasticsearch([app_web.config['ELASTICSEARCH_URL']]) \
        if app_web.config['ELASTICSEARCH_URL'] else None

    print(app_web.config['MAIL_SERVER'])
    if not app_web.debug and not app_web.testing:
        if app_web.config['MAIL_SERVER']:
            auth = None
            if app_web.config['MAIL_USERNAME'] or app_web.config['MAIL_PASSWORD']:
                auth = (app_web.config['MAIL_USERNAME'], app_web.config['MAIL_PASSWORD'])
            secure = None
            if app_web.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app_web.config['MAIL_SERVER'], app_web.config['MAIL_PORT']),
                fromaddr='no-reply@' + app_web.config['MAIL_SERVER'],
                toaddrs=app_web.config['ADMINS'], subject='NailMasterKrd',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app_web.logger.addHandler(mail_handler)
    
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/nail.log', maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app_web.logger.addHandler(file_handler)
    
        app_web.logger.setLevel(logging.INFO)
        app_web.logger.info('Nail startup')

    return app_web


#@babel.localeselector
#def get_locale():
#    return request.accept_languages.best_match(app_web.config['LANGUAGES'])

@babel.localeselector
def get_locale():
    # return request.accept_languages.best_match(app.config['LANGUAGES'])
    return 'ru'


from app import models

