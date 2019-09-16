from flask import render_template, flash, redirect, url_for, request
from app.news import bp
from app import db
from app.news.models import News

@bp.route('/')
def index():
    news_list = News.query.order_by(News.published.desc()).all()
    return render_template("news/index.html", news_list=news_list)