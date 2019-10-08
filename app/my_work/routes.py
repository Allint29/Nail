from flask import render_template, flash, redirect, url_for, request
from app.my_work import bp
from app import db
from app.user.models import User
from app.my_work.models import MyWork, CommentsToMyWorks
from app.my_work.forms import CommentForm, ChangeCommentToMyWorkForm
from flask_login import current_user, login_required;
from app.main_func import utils
import operator
from flask_babel import _, get_locale

@bp.route('/')
def index():

    work_list = MyWork.query.order_by(MyWork.published.desc()).all()

    comment_forms_list = []  

    for work in work_list:
        comment_form = CommentForm(work_id = work.id)      
        comment_forms_list.append({'work' : work, 'comment_form' : comment_form})


    return render_template("my_work/index.html", comment_forms_list = comment_forms_list)#work_list=work_list, comment_forms_list = comment_forms_list)


#R11Создадим обработчик который будет сохранять новый комментарий, если его не будет то удет выводиться ошибка
@bp.route('/comments', methods=['POST'])
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
            
            owner = User.query.filter_by(id=current_user.id).first()
            owner = owner.username
            comment = CommentsToMyWorks(id_site="0", media = "", owner = owner, show=1, text=form.comment_text.data, my_work_id=form.work_id.data, source="this")
                        
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


@bp.route('/comments/delete_comment/<comment_id>')
@login_required
def delete_comment(comment_id):
    '''
    view of form to delete comments
    '''
    #Если комментарий не с этого сайта, то его можно удалить только админу
    this_comment = CommentsToMyWorks.query.filter_by(id = comment_id).first()

    if current_user.is_admin:
            this_comment.hide_comment()
            db.session.commit()
            flash('Комментарий удален!')
            return redirect(utils.get_redirect_target())
    else:        
        if this_comment.source != "this":
                user = User.query.filter_by(username=this_comment.owner).first()
                if current_user.id == user_id:
                    this_comment.hide_comment()
                    db.session.commit()
                    flash('Комментарий удален!')
                    return redirect(utils.get_redirect_target())
                return redirect(utils.get_redirect_target())      

@bp.route('/comments/change_comment/<comment_id>', methods=['GET', 'POST'])
@login_required
def change_comment(comment_id):
    '''
    view of form to delete comments
    '''
    #Если комментарий не с этого сайта, то его можно изменить только админу
    this_comment = CommentsToMyWorks.query.filter_by(id = comment_id).first()
    form = ChangeCommentToMyWorkForm(this_comment.id, text = this_comment.text)

    if form.validate_on_submit():    
         if current_user.is_admin:                 
                 this_comment.text = form.text.data
                 db.session.commit()
                 flash(_('Комментарий изменен!'))          
                 return redirect(url_for('my_work.index'))                 
         else:        
             if this_comment.source != "this":
                     user = User.query.filter_by(username=this_comment.owner).first()
                     if current_user.id == user_id:
                         this_comment.text = form.text.data                         
                         db.session.commit()
                         flash(_('Комментарий изменен!'))
                         return redirect(url_for('my_work.index'))  
                     return redirect(url_for('my_work.index'))       
    elif request.method == 'GET':
        form.text = this_comment.text        

    return render_template('my_work/edit_comment.html', title=_('Изменение комментария'), form=form)

