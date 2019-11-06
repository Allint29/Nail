from flask import render_template, url_for, redirect, request
from app.admin_my import bp
from app.decorators.decorators import admin_required
from flask_babel import _
from app.admin_my.forms import AdminMenu, EditUsersForm, EditUsersPhoneForm
from app.user.models import User, UserPhones, ConnectionType

@bp.route('/', methods=['GET', 'POST'])
@admin_required
def admin_index():
    '''
    Страница распределения маршрутов админки
    '''
    titleVar='Панель админа'
    form_admin_menu = AdminMenu()

    if form_admin_menu.to_schedule.data:        
        return redirect(url_for('master_schedule.show_schedule_master'))

    if form_admin_menu.to_users.data:        
        return redirect(url_for('admin_my.edit_users_form', index_client = "-1"))

    return render_template('admin_my/index.html', title=titleVar, form_admin_menu=form_admin_menu)

@bp.route('/edit_users_form<index_client>', methods=['GET', 'POST'])
@admin_required
def edit_users_form(index_client):
    '''
    Вывод страницы редактирования клиентов
    '''
    titleVar='Редактирование клиентов'
    list_edit_users_form = []
    index_client = int(index_client)

    if request.method == "POST":
        pass
    elif request.method == "GET":
        if index_client < 0:
            users =  User.query.all()
            for u in users:
                conection_type = ConnectionType.query.filter(ConnectionType.id == u.connection_type_id).first()

                edit_users_form = EditUsersForm()
                list_phones = {}
              #  edit_users_form = EditUsersForm(request.POST, obj=u)

                edit_users_form.id_user.data = u.id
                edit_users_form.username_field.data=u.username
                edit_users_form.about_me_field.data =  u.about_me
                edit_users_form.email_field.data = u.email
                if u.email_confirmed == 0:
                    edit_users_form.email_confirmed_field.data = "0"
                else:
                    edit_users_form.email_confirmed_field.data = "1"                
                edit_users_form.registration_date_field.data = u.registration_date  
                edit_users_form.trying_to_enter_new_phone_field.data = u.trying_to_enter_new_phone
                
                if u.role == 'admin':
                    edit_users_form.role_field.data = 'admin'
                else:
                    edit_users_form.role_field.data = 'user'
               
                edit_users_form.last_seen_field.data = u.last_seen
                if conection_type:
                    edit_users_form.type_connection_field.data=conection_type.name_of_type               
                
                for p in u.phones:
                    form_phone = EditUsersPhoneForm()
                    form_phone.id_phone.data = p.id
                    form_phone.number_phone_field.data = p.number
                    form_phone.black_list_field.data = p.black_list
                    form_phone.phone_confirmed_field.data = p.phone_checked
                    form_phone.date_to_expire_field.data = p.expire_date_hash

                    list_phones={ p : form_phone}

              #  phones= u.phones
              #  choices = []
              #  for p in phones:
              #      choices.append((p.id, p.number))                    
              #  #print((s.id) for s in choices)
              #  edit_users_form.phones.choices = choices
              #  #edit_users_form.phones.choices = [(p.id, p.number) for p in UserPhones.query.filter(UserPhones.user_id == u.id).order_by('number')]
                

                #edit_users_form.phones.data = u.phones



                list_edit_users_form.append((edit_users_form, list_phones))           


        return render_template('admin_my/edit_users.html', title=titleVar, list_edit_users_form=list_edit_users_form)