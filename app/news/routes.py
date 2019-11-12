from flask import render_template, flash, redirect, url_for, request, current_app
from app.news import bp
from app import db
from app.news.models import News, CommentsToNews
from app.my_work.models import MyWork
from app.news.forms import CommentForm;
from flask_login import current_user, login_required;
from flask_babel import _, get_locale
from app.main_func import utils
import random

@bp.route('/news')
def index():
    news_list = News.query.filter(News.text.isnot("")).filter(News.text.isnot(None)).order_by(News.published.desc()) #.all()
    work_list = MyWork.query.order_by(MyWork.published.desc()).all()

    page = request.args.get('page')
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1

    last_pict = random.randint(5, len(work_list))
    work_list = work_list[last_pict-5 : last_pict]

    pages_new = news_list.paginate(page=page, per_page=3)   

    next_url = url_for('news.index', page=pages_new.next_num) if pages_new.has_next else None
    prev_url = url_for('news.index', page=pages_new.prev_num) if pages_new.has_prev else None


    return render_template("news/index.html", news_list=news_list, work_list=work_list, pages=pages_new, next_url=next_url, prev_url=prev_url)

#после мы по этому номеру ищем в Id новости саму новость
@bp.route('/<int:news_id>')
def single_news(news_id):
    my_news = News.query.filter(News.id == news_id).first();
    news_list = News.query.order_by(News.published.desc()).all()[0:3];           
    if not my_news:
        abort(404);    
    comment_form = CommentForm(news_id=my_news.id);
    return render_template('news/single_news.html', page_title=my_news.title, news = my_news, news_list=news_list, comment_form = comment_form);


#R11Создадим обработчик который будет сохранять новый комментарий, если его не будет то удет выводиться ошибка
@bp.route('/news/comments', methods=['POST'])
@login_required
def add_comment():
    '''
    func added comment to BD from web of single news
    '''
    form = CommentForm();
    if form.validate_on_submit():
            comment = CommentsToNews(text=form.comment_text.data, news_id=form.news_id.data, user_id=current_user.id)
            db.session.add(comment)
            db.session.commit();
            flash(_('Спасибо за комментарий!'));
    else:            
             for field, errors in form.errors.items():
                 for error in errors:                   
                     flash(_('Ошибка в поле') + f' "{getattr(form, field).label.text}": {error}')
     #R11 после объявления всех ошибок переадресуем на ту же страницу с которой он давалкомментарий - это плохой способ, 
     # так как адремс можно подложить другой, например атакующего
    #return redirect(request.referrer)
    #используем наш валидатор на подлинность ссылки
    return redirect(utils.get_redirect_target())