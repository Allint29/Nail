# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from flask import render_template, flash, redirect, url_for, request, g, \
        jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.main_func import utils as main_utils
from app.user.main.forms import EditProfileForm, EditProfilAddPhoneForm, PostForm, SearchForm, \
    CreateNewEmail, CreateNewEmailCongratulation, CreateNewPassword
from app.user.models import User, Post, UserPhones
from app.user.utils import delete_non_comfirmed_phone, step_one_for_enter_phone, step_two_for_enter_phone, \
    cancel_user_phone, delete_user_phone, delete_non_comfirmed_email
from app.main_func.translate import translate
from app.user.myemail import send_mail_reset_email
from app.user.main import bp


################################################ Функционал подписи на пользователей и поиска и перевода по сайту ###########################################

@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    #print('!!!!!!!!!!!')
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})

@bp.route('/follow_<username>')
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
    try:
        db.session.commit()
        flash('Вы подписаны {}!'.format(username))
    except:
        pass
    return redirect(url_for('main.user', username=username))

@bp.route('/unfollow_<username>')
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
    try:
        db.session.commit()
        flash(_('Вы отписаны от пользователя %(username)s.', username=username))
    except:
        pass
    return redirect(url_for('main.user', username=username))


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
    ''',
    
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

################################################################################################################################


################################################# Блок личного пространства пользователя - посты ###################################

#@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    '''
    маршрут к станице пользователя, в которой он может писать посты
    '''
    titleVar=_('Домашняя страница')
    helo=_('Вы на главной странице своего профиля.')
    form = PostForm()    
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data, author=current_user, language=language)
        try:
            db.session.add(post)        
            db.session.commit()
            flash(_('Ваш пост опубликован!'))
        except:
            pass
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    
    return render_template('user/index.html', title=titleVar, form=form, pages=posts, next_url=next_url, helllo=helo,
                           prev_url=prev_url)


@bp.route('/explore')
@login_required
def explore():
    '''
    маршрут к страничке общего вывода всех постов
    '''
    titleVar=_('Обзор')
    helo=_('Вы в общем чате сайта.')
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('user/index.html', title=titleVar, pages=posts, next_url=next_url, prev_url=prev_url, helllo=helo)


@bp.route('/<username>')
@login_required
def user(username):
    '''
    маршрут к странице пользователя и его постам
    '''
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user/user.html', user=user, pages=posts.items,
                           next_url=next_url, prev_url=prev_url)

################################################################################################################################

################################################ Редактирование профиля пользователя ###########################################

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    list_phones_user = UserPhones.query.filter_by(user_id = current_user.id).all()
    e_mail = current_user.email 
    e_mail_to_send = None
    if current_user.email:
        e_mail_to_send = current_user.email
    else:
        e_mail_to_send = main_utils.default_email()
        
    if form.validate_on_submit():
        if form.submit.data:            
            current_user.username = form.username.data
            current_user.about_me = form.about_me.data
            try:
                db.session.commit()
                flash(_('Ваши изменения в профиле были сохранены.'))
            except:
                pass
            return redirect(url_for('main.edit_profile'))
        if form.phone_button.data:           
            flash(_('Вы направлены на страничку редактирования телефонов.'))
            return redirect(url_for('main.edit_profile_add_phone')) 
        if form.email_button.data or form.email_change_button.data:
            delete_non_comfirmed_email()
            flash(_('Вы направлены на страничку редактирования адреса электронной почты.'))
            return redirect(url_for('main.edit_profile_add_email', mail=e_mail_to_send)) 
        if form.change_password_button.data:            
            flash(_('Вы направлены на страничку смены пароля.'))
            return redirect(url_for('main.edit_profile_change_password', user=current_user.username)) 


    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('user/edit_profile/edit_profile.html', title=_('Редактирование профиля'), form=form, \
        list_phones_user=list_phones_user, e_mail=e_mail)

@bp.route('/edit_profile_add_phone', methods=['GET', 'POST'])
@login_required
def edit_profile_add_phone():
    form = EditProfilAddPhoneForm(current_user.id)
    list_phones_user = UserPhones.query.filter_by(user_id = current_user.id).all()
    number_for_check = None
    if list_phones_user:
        for number in list_phones_user:
            if number.phone_checked == 0:
                number_for_check = number
                break
               
    if form.validate_on_submit():        
        #выслать смс для подтверждения нового телефона
        if form.submit.data:  
            step_one_for_enter_phone(form.number_phone.data, current_user.id)
            return redirect(url_for('main.edit_profile_add_phone'))        

        #поддтвердить ввод высланного кода
        elif form.commit_confirm.data:
            step_two_for_enter_phone(number_for_check, form.code_of_confirm.data)  
            return redirect(url_for('main.edit_profile_add_phone'))
        
        #отмена подтверждения телефона
        elif form.phone_button_cancel.data:
            #удаляем номер из БД
            cancel_user_phone(number_for_check)           
            return redirect(url_for('main.edit_profile_add_phone'))

        #удаение введенного номера телефона
        elif form.phone_button_delete.data:            
            delete_user_phone(current_user.id, form.number_phone.data, list_phones_user)  
            return redirect(url_for('main.edit_profile_add_phone'))
        
    elif request.method == 'GET':
        delete_non_comfirmed_phone()        
        if number_for_check:
            form.number_phone.data = number_for_check.number
        else:
            form.number_phone.data = ""

    return render_template('user/edit_profile/edit_profile_add_phone.html', title=_('Добавление номера телефона'), form=form, list_phones_user = list_phones_user, number_for_check = number_for_check)

@bp.route('/edit_profile_add_email_<mail>', methods=['GET', 'POST'])
@login_required
def edit_profile_add_email(mail):
    form = CreateNewEmail()
    delete_non_comfirmed_email()
    if form.validate_on_submit():
            if form.confirm_registration.data:
                if form.email.data == main_utils.default_email():
                     flash(_('Введите действующий адрес.'))
                     return redirect(url_for('main.edit_profile_add_email', mail=mail))
                if form.email.data == current_user.email:
                     flash(_('Ваша почта уже зарегистрирована.'))
                     return redirect(url_for('main.edit_profile', mail=mail))
                current_user.bufer_email = form.email.data
                current_user.expire_date_request_bufer_mail = datetime.utcnow() + timedelta(seconds = current_app.config['SECONDS_TO_CONFIRM_EMAIL'])
                try:
                    db.session.commit()
                except:
                    pass
                    #print (form.email.data)
                    #print (current_user)
                try:
                    send_mail_reset_email(current_user, form.email.data)
                    flash(_('Вам на почту выслано письмо со ссылкой для подтверждения регистрации.'))
                except:
                    pass

                return redirect(url_for('main.edit_profile'))
            else:
                flash(_('Вы отменили операцию добавления адреса электронной почты.'))
                return redirect(url_for('main.edit_profile'))
            
    elif request.method == 'GET':
        
        form.username.data=current_user.username
        if mail is None:            
            form.email.data = main_utils.default_email()
        elif mail == main_utils.default_email():            
            form.email.data = main_utils.default_email()
        else:
            form.email.data = current_user.email

    return render_template('user/edit_profile/edit_profile_new_email.html', title=_('Редактирование профиля'), form=form, \
        user=current_user, mail=mail)

@bp.route('/edit_profile_add_email_confirm_<token>', methods=['GET', 'POST'])
def confirm_adding_email(token):
    '''
    view of finish of registration new user, create new pass and redirect to login
    '''
    titleVar=_('Подтверждение электронной почты')
    flash_user_register=_('Ваша почта подтверждена!')
    #if current_user.is_authenticated:
    #    return redirect(url_for('main.index'))
    user = User.verify_new_registration_token(token)

    if not user:
        print('Почта не подтверждена. Что-то пошло не так...')
        flash(_('Почта не подтверждена. Что-то пошло не так...'))
        return redirect(url_for('main.index'))

    form = CreateNewEmailCongratulation()    
    if form.validate_on_submit():
        user.email = user.bufer_email
        user.bufer_email = None
        user.expire_date_request_bufer_mail = main_utils.min_date_for_calculation()
        user.set_confirm_email_true()      
        try:
            db.session.add(user)
            db.session.commit()
            flash(flash_user_register)
            #print('Зарегили')
        except:
            pass
        return redirect(url_for('main.edit_profile'))

    return render_template('user/edit_profile/edit_profile_new_email_congratulation.html', title=titleVar, form=form)

@bp.route('/edit_profile_change_password_<user>', methods=['GET', 'POST'])
@login_required
def edit_profile_change_password(user):
    titleVar=_('Смена пароля')
    flash_change_pass = _('Ваш пароль изменен.')
    form = CreateNewPassword()

    if form.validate_on_submit():
        if not current_user.check_password(form.old_password.data) or current_user.password_hash is None or current_user.password_hash == "":
            flash(_('Неправильно введен старый пароль'))
            return redirect(url_for('main.edit_profile'))

        current_user.set_password(form.password.data)
        try:
            db.session.commit()
            flash(flash_change_pass)
        except:
            pass
        return redirect(url_for('main.edit_profile'))

    
    return render_template('user/edit_profile/edit_profile_new_password.html', title=titleVar, form=form)




################################################################################################################################


