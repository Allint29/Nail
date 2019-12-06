#модуль нужен чтобы из командной строки задавать пользователя
#getpass очень похож на input - просить польз№ователя ввести что-то в ком строке
#это похоже на это только он не печатает то что пользователь вводит ***
from getpass import getpass;
#модуль взаимод с системными функц оттуда будем использовать sys.exit чтобы правильно завершать наш скрипт когда возникнет ошибка,
#чтобы не делать просто return
import sys;
#импортируем наш функции
from app import db, create_app
from app.user.models import User;

#запускаем весь процесс
app = create_app();

#после ввода этой строки станет доступна работа с БД
with app.app_context():
    username = input("Введите имя пользователя: ");

    if User.query.filter(User.username == username).count() > 0:
        print("Такой пользователь уже есть в базе.");
        sys.exit(0);

    password = getpass("Введите пароль: ");
    password2 = getpass("Введите пароль второй раз: ");

    if not password == password2:
        sys.exit(0);

    new_user = User(username=username, role="admin", connection_type_id = -1, user_from_master = 1);
    new_user.set_password(password);

    db.session.add(new_user);
    db.session.commit();
    print(f"Учетная запись {new_user.username} внесена в базу с правами администратора");
