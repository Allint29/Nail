import re
import json
import random
from app.user.models import User

def set_default_password_admin():
    '''
    Метод создает пароль для пользователя по умолчанию
    user - может быть передан объект или имя
    ''' 
    chars_for_pass = 'abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    len_choice = len(chars_for_pass) - 1
    length_pass = 7
    default_password = ""

    for i in range(length_pass):
        num_char = random.randint(0, len_choice)
        default_password = default_password + chars_for_pass[num_char]

    #print(default_password)
    
    if default_password is None or default_password=="":
        print('user_password')
        return 'user_password', False

    print(default_password)
    return str(default_password), True
