import os
from flask import Flask, render_template, request, redirect, session


from core.db import Db
from main import parsing
from data import db_session
from data.users import User
from prepare_dir import prepare
from forms.register_user import RegisterForm
from forms.loginform import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route("/form_load", methods=['POST', 'GET'])
def load_form():
    if request.method == 'GET':
        return render_template("load_form.html")
    else:
        if "uploads" not in os.listdir():
            os.mkdir("./uploads")
        files = request.files.getlist("dir")
        lst = os.listdir("./uploads")
        if len(lst):
            for i in lst:
                os.rmdir(i)
        for file in files:
            file.save(f"./uploads/{file.filename}")
        prepare()
        parsing()
        return redirect("/result")


@app.route("/result")
def output_result():
    db = Db()
    res = db.select("data_of_switchs", "SwitchName, FabricName")
    d = {}
    for i in res:
        tables = db.select("sqlite_master", "name", True, "type=\"table\" AND "
                                                      f"tbl_name LIKE '%{i[1]}_{i[0]}%'")
        d[f"{i[0]}"] = list(map(lambda x: x[0].replace(f"_{i[1]}_{i[0]}", ""), tables))
    return render_template("switchs.html", data=d)


@app.route("/result/<switchname>/<table_name>")
def output_res_of_switch(switchname, table_name):
    db = Db()
    table_name = db.select("sqlite_master", "name", True, "type=\"table\" AND "
                                                      f"tbl_name LIKE '%{table_name}%{switchname}%'")[0][0]
    res = db.select(table_name, "*")
    columns = list(map(lambda x: x[1], db.get_table_columns(table_name)))
    return render_template("info_table.html", columns=columns, data=res)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session["data"] = request.form
        return redirect("/form_load")
    return render_template("login.html", title="Авторизация", form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/")
def redirect_to_login():
    return redirect("/login")


def main():
    db_session.global_init("db/users.db")
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
