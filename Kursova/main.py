import plotly
import plotly.graph_objs as go
import json
from datetime import datetime

from flask import render_template, flash, request, redirect, session
from Model import *
from WTForms import *

app.secret_key = 'development key'

# currentUser = open('user.txt', 'w')
# currentUser.write("god_usop")
# currentUser.close()

def setCurrentUser(login):
    us = open('user.txt', 'w')
    us.write(login)
    us.close()

def CurrentUser():
    us = open('user.txt', 'r')
    nam = us.read()
    us.close()
    return nam

@app.route('/', methods=['GET', 'POST'])
def index():

    return render_template('index.html', userName=CurrentUser())

@app.route('/search', methods=['GET', 'POST'])
def search():

    form = RequestsForm()

    if request.method == 'POST':
        if not form.validate():
            flash('All fields are required')
            print("aaaaa")
            return render_template('search.html', form=form)
        else:
            user = Buildings.query.filter_by(numb_building=form.building.data).first()
            if user is not None:
                print("sssssss")
                if (user.numb_building.replace(' ', '') != form.building.data) and (101 >= form.building.data >= 121):
                    print("dddddd")
                    return render_template('search.html')
                else:
                    print("ffffffff")
                    now = datetime.now()
                    countId = len(Requests.query.filter_by().all())
                    print(countId)
                    requestq = Requests(
                        id=countId + 1,
                        login=CurrentUser(),
                        building=form.building.data,
                        audience=form.audience.data,
                        data='{}-{}-{}'.format(now.year, now.month, now.day),
                        time='{}:{}:{}'.format(now.hour, now.minute, now.second)
                    )
                    db.session.add(requestq)
                    db.session.commit()
                    mapForm = RequestsForm()
                    mapForm.building.data = form.building.data
                    mapForm.audience.data = form.audience.data
                    return render_template('map.html', form=mapForm)
    return render_template("search.html", form=form)


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    form = UsersForm()
    return render_template('sign_up.html', form=form)

@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    form = SingInForm()
    if request.method == 'POST':
        print("8")
        if not form.validate():
            flash('All fields are required')
            print("7")
            return render_template('sign_in.html', form=form)
        else:
            print("6")
            user = Users.query.filter_by(login=form.login.data).first()
            if user is not None:
                print("5")
                if user.password.replace(' ', '') != form.password.data:
                    print("4")
                    return render_template('sign_in.html', form=form)
                else:
                    setCurrentUser(user.login)
                    form = RequestsForm()
                    print("3")
                    return render_template('search.html', form=form)
            else:
                if form.login.data == 'admin' and form.password.data == '321':
                    setCurrentUser(form.login.data)
                    print("2")
                    return render_template('admin.html')
    print("1")
    return render_template("sign_in.html", form=form)


@app.route('/edit_building', methods=['GET', 'POST'])
def edit_building():
    form = BuildingsForm()
    select_result = Buildings.query.filter_by().all()


    if request.method == 'POST':

        if not form.validate():
            flash('All fields are required')
            return render_template('edit_buildings.html', data=select_result, form=form)
        else:
            building = Buildings.query.filter_by(numb_building=form.numb_building.data).first()
            building.numb_building = form.numb_building.data
            building.json = form.json.data
            db.session.commit()
            return render_template("buildings.html", data=select_result, form=form)

    return render_template("buildings.html", data=select_result, form=form)


@app.route('/buildings', methods=['GET', 'POST'])
def buildings():

    form = BuildingsForm()
    select_result = Buildings.query.filter_by().all()

    if request.method == 'POST':

        selected_code = request.form.get('del')
        if selected_code is not None:
            selected_row = Buildings.query.filter_by(numb_building=selected_code).first()
            db.session.delete(selected_row)
            db.session.commit()
            select_result.remove(selected_row)
            return render_template('buildings.html', data=select_result, form=form)

        selected_code = request.form.get('edit')
        if selected_code is not None:
            selected_row = Buildings.query.filter_by(numb_building=selected_code).first()
            session['building_edit_pk_data'] = selected_code
            return render_template("edit_building.html", row=selected_row, form=form, error="Не коректновведені дані")

        if not form.validate():
            flash('All fields are required.')
            return render_template('buildings.html', data=select_result, form=form)
        else:
            if Buildings.query.filter_by(numb_building=form.numb_building.data).first() is None:
                building = Buildings(numb_building=form.numb_building.data,
                                     json=form.json.data)
                db.session.add(building)
                db.session.commit()
                select_result.append(building)
            else:
                return render_template('buildings.html', data=select_result, form=form, error="Дана будівля вже існує")


    return render_template('buildings.html', data=select_result, form=form)


@app.route('/edit_group', methods=['GET', 'POST'])
def edit_group():

    form = GroupsForm()
    select_result = Groups.query.filter_by().all()

    if request.method == 'POST':
        if not form.validate():
            flash('All fields are required.')
            return render_template('edit_group.html')
        else:
            number = session['group_edit_pk_data']
            group = Groups.query.filter_by(name_group=number).first()
            group.name_group = form.name_group.data
            return render_template("groups.html", data=select_result, form=form)

    return render_template("groups.html", data=select_result, form=form)


@app.route('/groups', methods=['GET', 'POST'])
def groups():

    form = GroupsForm()
    select_result = Groups.query.filter_by().all()

    if request.method == 'POST':

        selected_number = request.form.get('del')
        if selected_number is not None:
            selected_row = Groups.query.filter_by(name_group=selected_number).first()
            db.session.delete(selected_row)
            db.session.commit()
            select_result.remove(selected_row)
            return render_template('groups.html', data=select_result, form=form)

        selected_number = request.form.get('edit')
        if selected_number is not None:
            selected_row = Groups.query.filter_by(name_group=selected_number).first()
            session['group_edit_pk_data'] = selected_number
            return render_template("edit_group.html", row=selected_row, form=form)

        if not form.validate():
            flash('All fields are required.')
            return render_template('groups.html', data=select_result, form=form, error="Не коректновведені дані")
        else:
            if Groups.query.filter_by(name_group=form.name_group.data).first() is None:
                group = Groups(form.name_group.data)
                db.session.add(group)
                db.session.commit()
                select_result.append(group)
            else:
                render_template('groups.html', data=select_result, form=form, error="Дана група вже існує")

    return render_template('groups.html', data=select_result, form=form)


@app.route('/edit_user', methods=['GET', 'POST'])
def edit_user():

    form = UsersForm()
    select_result = Users.query.filter_by().all()

    if request.method == 'POST':
        if not form.validate():
            flash('All fields are required')
            return render_template('edit_user.html', data=select_result, form=form, error="Не коректновведені дані")
        else:
            user = Users.query.filter_by(login=form.login.data).first()
            user.login = form.login.data
            user.password = form.password.data
            user.numb_group = form.numb_group.data
            user.year = form.year.data
            db.session.commit()
            return render_template("users.html", data=select_result, form=form)

    return render_template("users.html", data=select_result, form=form,  error="Не коректновведені дані")


@app.route('/users', methods=['GET', 'POST'])
def users():

    form = UsersForm()
    select_result = Users.query.filter_by().all()

    if request.method == 'POST':

        selected_name = request.form.get('del')
        if selected_name is not None:
            selected_row = Users.query.filter_by(login=selected_name).first()
            db.session.delete(selected_row)
            db.session.commit()
            select_result.remove(selected_row)
            return render_template('users.html', data=select_result, form=form)

        selected_name = request.form.get('edit')
        if selected_name is not None:
            selected_row = Users.query.filter_by(login=selected_name).first()
            session['user_edit_pk_data'] = selected_name
            return render_template("edit_user.html", row=selected_row, form=form)

        if not form.validate():
            flash('All fields are required.')
            return render_template('sign_up.html', data=select_result, form=form, error="Не коректновведені дані")
        else:
            if Users.query.filter_by(login=form.login.data).first() is None:
                user = Users(
                    form.login.data,
                    form.password.data,
                    form.numb_group.data,
                    form.year.data
                )
                db.session.add(user)
                db.session.commit()
                select_result.append(user)
            else:
                return render_template('sign_up.html', data=select_result, form=form, error="Даний користувач вже існує")


    return render_template('users.html', data=select_result, form=form)

@app.route('/requests', methods=['GET', 'POST'])
def user():

    form = RequestsUserForm()
    if CurrentUser() == "admin":
        select_result = Requests.query.filter_by().all()
    else:
        select_result = Requests.query.filter_by(login=CurrentUser()).all()

    if request.method == 'POST':

        selected_name = request.form.get('del')
        if selected_name is not None:
            selected_row = Requests.query.filter_by(id=form.id.data).first()
            db.session.delete(selected_row)
            db.session.commit()
            select_result.remove(selected_row)
            return render_template('requests.html', data=select_result, form=form)

        selected_name = request.form.get('del_oll')
        if selected_name is not None:
            if CurrentUser() == "admin":
                selected_row = Requests.query.filter_by().all()
            else:
                selected_row = Requests.query.oll().filter_by(login=CurrentUser())

            db.session.delete(selected_row)
            db.session.commit()
            select_result.remove(selected_row)
            return render_template('requests.html', data=select_result, form=form)

    return render_template('requests.html', data=select_result, form=form)


if __name__ == '__main__':
    app.run(debug=True)