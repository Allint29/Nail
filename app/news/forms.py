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

class CommentForm(FlaskForm):
    '''
    model of input comments for news
    '''
    news_id = HiddenField('ID новости', validators=[DataRequired()]);
    comment_text = StringField('Текст комментария', validators=[DataRequired()], render_kw={"class" : "form-control"});
    submit = SubmitField('Отправить', render_kw={"class": "btn btn-primary"});

    #R11 проверки на то что новость существует в БД лучше сделать из класса самой формы новости
    def validate_news_id(self, news_id):
        if not News.query.get(news_id.data):
            raise ValidationError('Новости с таким id не существует.')

    
