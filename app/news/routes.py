from flask import render_template, flash, redirect, url_for, request
from app.news import bp

@bp.route('/')
def index():
    return render_template("news/index.html")