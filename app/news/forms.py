from flask_wtf import FlaskForm;
#импортируем типы полей - классы типов
#R4 для запоминания залогиненого пользователя есть модуль BooleanField
from wtforms import HiddenField, StringField, SubmitField
#импортируем валидатор - класс помогает избежать ручных проверок
#например если польз отправил пустые данные мне не нужно проверять это в 
#ручную валидатор это сделает за меня автоматически
#R7 для создания своих валидаторов нужно импортировать ValidationError
from wtforms.validators import DataRequired, ValidationError

#мипортируем, та как мы будеем проверять id новости
from app.news.models import News
from flask_babel import Babel, _, lazy_gettext as _l

class CommentForm(FlaskForm):
    '''
    model of input comments for news
    '''
    news_id = HiddenField('ID новости', validators=[DataRequired()]);
    comment_text = StringField(_('Оставьте комменарий'), validators=[DataRequired()], render_kw={"class" : "form-control comment-field", "placeholder" : _('Оставьте комментарий')});
    submit = SubmitField(_('Отправить'), render_kw={"class": "button"});

    #R11 проверки на то что новость существует в БД лучше сделать из класса самой формы новости
    def validate_news_id(self, news_id):
        if not News.query.get(news_id.data):
            raise ValidationError(_('Новости с таким id не существует.'))

    
