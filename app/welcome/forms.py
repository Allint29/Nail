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
