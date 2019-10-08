from flask import render_template, flash, redirect, url_for, request, current_app
from app.news import bp
from app import db
from app.news.models import News, CommentsToNews
from app.my_work.models import MyWork
from app.news.forms import CommentForm;
from flask_login import current_user, login_required;
from flask_babel import _, get_locale
from app.main_func import utils

@bp.route('/')
@bp.route('/news')
def index():
    news_list = News.query.filter(News.text.isnot("")).filter(News.text.isnot(None)).order_by(News.published.desc()).all()
    work_list = MyWork.query.order_by(MyWork.published.desc()).all()

    return render_template("news/index.html", news_list=news_list, work_list=work_list)

#после мы по этому номеру ищем в Id новости саму новость
@bp.route('/<int:news_id>')
def single_news(news_id):
    my_news = News.query.filter(News.id == news_id).first();
    news_list = News.query.order_by(News.published.desc()).all();
    
           
    if not my_news:
        abort(404);    
    #R11добавляем экземпляр формы комментария и передаем в шаблон
    #R11 для того чтобы при создании формы поле автоматически заполнялось нужно передать параметр в эту форму
    #R11 здесь мы передаем id новости чтобы далее ееобработать в БД
    comment_form = CommentForm(news_id=my_news.id);
    return render_template('news/single_news.html', page_title=my_news.title, news = my_news, news_list=news_list, comment_form = comment_form);


#R11Создадим обработчик который будет сохранять новый комментарий, если его не будет то удет выводиться ошибка
@bp.route('/news/comments', methods=['POST'])
#R11 для того чтобы незарегиный пользователь не мог оставлять комментарии  нужно сделать 
# проверку на это для этого импортируем
@login_required
def add_comment():
    '''
    func added comment to BD from web of single news
    '''
    form = CommentForm();
    #R11 делаем проверку на то что форма провалидирована то... 
    if form.validate_on_submit():
        #R11 проверим, что новость действительно есть в БД
        #R11 проверки на то что новость существует в БД лучше сделать из класса самой формы новости
        #R11if News.query.filter(News.id == form.news_id.data).first():
            #R11 создаем переменную коментария и сохр ее в БД
            comment = CommentsToNews(text=form.comment_text.data, news_id=form.news_id.data, user_id=current_user.id)
            db.session.add(comment)
            db.session.commit();
            flash(_('Спасибо за комментарий!'));
    else:            
             #R11 даем исключения конечному пользователю какая именно ошибка при добавлении коментария
             for field, errors in form.errors.items():
                 for error in errors:
                   #  flash(f'Ошибка в поле "{getattr(form, field).label.text}": {error}')
                     flash(_('Ошибка в поле') + f' "{getattr(form, field).label.text}": {error}')
     #R11 после объявления всех ошибок переадресуем на ту же страницу с которой он давалкомментарий - это плохой способ, 
     # так как адремс можно подложить другой, например атакующего
    #return redirect(request.referrer)
    #используем наш валидатор на подлинность ссылки
    return redirect(utils.get_redirect_target())