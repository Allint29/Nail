from flask_wtf import FlaskForm;
#импортируем типы полей - классы типов
#R4 для запоминания залогиненого пользователя есть модуль BooleanField
from wtforms import HiddenField, StringField, SubmitField, TextAreaField
#импортируем валидатор - класс помогает избежать ручных проверок
#например если польз отправил пустые данные мне не нужно проверять это в 
#ручную валидатор это сделает за меня автоматически
#R7 для создания своих валидаторов нужно импортировать ValidationError
from wtforms.validators import DataRequired, ValidationError, Length
from flask_babel import Babel, _, lazy_gettext as _l

#мипортируем, та как мы будеем проверять id новости
from app.my_work.models import MyWork

class CommentForm(FlaskForm):
    '''
    model of input comments for news
    '''
    work_id = HiddenField('ID работы', validators=[DataRequired()]);
    comment_text = TextAreaField(_l('Оставьте отзыв!'), validators=[DataRequired()], render_kw={"class" : "form-control comment-field", "placeholder": _l("Оставьте отзыв!")});
    submit = SubmitField(_l('Отправить'), render_kw={"class": "button"});

    #R11 проверки на то что новость существует в БД лучше сделать из класса самой формы новости
    def validate_work_id(self, work_id):
        if not MyWork.query.get(work_id.data):
            raise ValidationError('Работы с таким id не существует.')

   # def validate_work_to_show(self, work_show):
   #     if MyWork.query.get(work_show.data) == 0:
   #         raise ValidationError('Данного комментария не существует.')

class ChangeCommentToMyWorkForm(FlaskForm):
    '''
    class for visualisation form for insert some changes in comment of user.
    '''    
    comment_text = TextAreaField(_l('Отредактируйте комментарий'), validators=[Length(min=0, max=140)], render_kw={"class" : "form-control comment-field", "placeholder": _l('Внесите изменения в свой комментарий.')})
    submit = SubmitField(_l('Опубликовать'),  render_kw={"class": "button"})

    def __init__(self, original_comment_id, *args, **kwargs):
        super(ChangeCommentToMyWorkForm, self).__init__(*args, **kwargs)
        self.original_comment_id = original_comment_id
