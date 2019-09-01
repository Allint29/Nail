# -*- coding: utf-8 -*-
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
        jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.main.forms import EditProfileForm, PostForm, SearchForm
from app.models import User, Post
from app.translate import translate
from app.main import bp


@bp.before_app_request
def before_request():
    '''
    func record last trequest from user to line of record user in user-table
    '''
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        print(form.post.data)
        print(language)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Ваш пост живой!'))
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Домашняя страница'), form=form, posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Обзор'), posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Ваши изменения в форме были сохранены.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Редактирование профиля'), form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    '''
    view of form to folow to user
    '''
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('Пользователь %(username)s не найден.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('Вы отписаны от пользователя %(username)s.', username=username))
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('Вы подписаны {}!'.format(username))
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('Пользователь %(username)s не найден.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('Вы не можете отписаться от самого себя!'))
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('Вы отписаны от пользователя %(username)s.', username=username))
    return redirect(url_for('main.user', username=username))



@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})

@bp.before_app_request
def before_request():
    '''
    В приведенном коде я создаю экземпляр класса формы поиска, 
    когда у меня есть аутентифицированный пользователь. И, конечно, 
    мне необходимо, чтобы этот объект формы сохранялся до тех пор, пока 
    он не будет отображен в конце запроса, поэтому мне нужно где-то его сохранить. 
    Это где-то будет контейнером g, предоставленным Flask. Переменная g, 
    предоставленная Flask, является местом, где приложение может хранить данные, 
    которые должны сохраняться в течение всего срока службы запроса. Я храню форму 
    в g.search_form, поэтому, когда обработчик запроса before заканчивается и Flask 
    вызывает функцию представления, которая обрабатывает запрошенный URL, объект g 
    будет таким же, и все равно будет иметь форму, прикрепленную к нему. Важно отметить,
    что эта переменная g специфична для каждого запроса и каждого клиента, поэтому, 
    даже если ваш веб-сервер обрабатывает несколько запросов одновременно для разных 
    клиентов, вы все равно можете полагаться на g для работы в качестве частного 
    хранилища для каждого запроса, независимо от того, что происходит в других запросах,
    которые обрабатываются одновременно.
    '''
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())

@bp.route('/search')
@login_required
def search():
    '''
    Вы видели, что в других формах я использовал метод form.validate_on_submit(),
    чтобы проверить, является ли представление формы действительным. К сожалению, 
    этот метод работает только для форм, представленных через запрос POST, поэтому для 
    этой формы мне нужно использовать form.validate(), который просто проверяет значения полей, 
    не проверяя, как данные были отправлены. Если проверка не удалась, это связано с тем, 
    что пользователь отправил пустую форму поиска, поэтому в этом случае я просто перенаправляюсь 
    на страницу исследования, в которой отображаются все сообщения в блоге.
    
    Метод Post.search() из моего класса SearchableMixin используется для получения списка 
    результатов поиска. Разбиение на страницы обрабатывается очень похожим образом на 
    индексирование и просмотр страниц, но создание следующей и предыдущей ссылок немного 
    сложнее без помощи объекта Pagination из Flask-SQLAlchemy. Здесь полезно использовать 
    общее количество результатов, переданных как второе возвращаемое значение из Post.search().
    '''
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    #переопределяю переменную на определение нашедшихся данных ксли возвращается словарь то беру поле словаря, если число само число
    #почему-то в разных вариантах ведет себя по разному
    totalVal = 50

    if type(total) is not int:
        totalVal = total['value']
    elif type(total) is int:
        totalVal = total

    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if totalVal > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title=_('Поиск'), posts=posts,
                           next_url=next_url, prev_url=prev_url)