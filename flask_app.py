from flask_login import LoginManager, login_required, login_user, logout_user, current_user
import os
from werkzeug.utils import redirect
from data import db_session
from flask import Flask, render_template, request
from data.users import User
from data.valutes import Valute
from forms.login import LoginForm
from forms.register import RegisterForm
import random
from PIL import Image
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
valutes_names = ['NEAR', 'Bitcoin', 'Fynjycoin', 'Saratovcoin',
                 'Agrocoin', 'euro', 'dollar', 'rubl']
valutes_names_human = ['NEAR', 'Bitcoin', 'Fynjycoin', 'Saratovcoin',
                       'Agrocoin', 'Евро', 'Доллар', 'Рубль']


def update_volatil():
    try:
        valute_request = "http://api.currencylayer.com/live?access_key=3638b82d0bdfa7177bf3ea5551bde83f&format=1"
        response = requests.get(valute_request)
        response = response.json()["quotes"]
    except Exception:
        response = {}

    db_sess = db_session.create_session()
    p = db_sess.query(Valute).all()
    for i in p:
        try:
            i.volatil = response[i.sovalute_name]
        except Exception:
            i.volatil = max(1, i.volatil + random.randint(-2, 2) / 10)
    db_sess.commit()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают")
        db_session.global_init('db/fynjynance.db')
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(name=form.name.data, surname=form.surname.data, email=form.email.data,
                    phone=form.phone.data)
        user.set_password(form.password.data)

        form.photo.data.save('static/profile_photos/' + form.email.data.replace('.', '') + '.jpg')
        original_image = Image.open('static/profile_photos/' + form.email.data.replace('.', '') + '.jpg')
        resized_image = original_image.resize((60, 60))
        resized_image.save('static/profile_photos/' + form.email.data.replace('.', '') + '.png')

        user.photo_way = '/static/profile_photos/' + form.email.data.replace('.', '') + '.png'

        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.errorhandler(404)
def not_found(error):
    return '<h1>Ваш кошелёк взломан, доставайте из кармана фламинго и покупайте билеты в тихий океан</h1>'


@app.route('/')
def home():
    if current_user.is_authenticated:
        return render_template('home.html')
    else:
        return redirect('/login')


@app.route('/actives')
def my_actives():
    db_sess = db_session.create_session()
    p = db_sess.query(User).filter(User.id == current_user.id).first()
    form = {'NEAR': p.NEAR,
            'Bitcoin': p.Bitcoin,
            'Fynjycoin': p.Fynjycoin,
            'Saratovcoin': p.Saratovcoin,
            'Agrocoin': p.Evgrocoin,
            'Евро': p.euro,
            'Долларов': p.dollar,
            'Рублей': p.rubl}
    db_sess.commit()
    return render_template("actives.html", form=form)


@app.route('/sell')
def sell():
    return render_template("sell.html", current_user=current_user, form=valutes_names_human)


@app.route('/sell/<valute1>/buy')
def buy(valute1):
    db_sess = db_session.create_session()
    p = db_sess.query(Valute).filter(Valute.name == valutes_names[valutes_names_human.index(valute1)]).first()
    db_sess.commit()
    return render_template("buy.html", form=valutes_names_human, valute1=valute1, way=p.img_direct)


@app.route('/sell/<valute1>/buy/<valute2>', methods=['POST', 'GET'])
def do_sell(valute1, valute2):
    update_volatil()
    if request.method == 'GET':
        db_sess = db_session.create_session()
        p1 = db_sess.query(Valute).filter(Valute.name == valutes_names[valutes_names_human.index(valute1)]).first()
        p2 = db_sess.query(Valute).filter(Valute.name == valutes_names[valutes_names_human.index(valute2)]).first()
        u = db_sess.query(User).filter(User.id == current_user.id).first()
        mx = 0
        if valute1 == "NEAR":
            mx = u.NEAR
        elif valute1 == "Bitcoin":
            mx = u.Bitcoin
        elif valute1 == "Fynjycoin":
            mx = u.Fynjycoin
        elif valute1 == "Saratovcoin":
            mx = u.Saratovcoin
        elif valute1 == "Agrocoin":
            mx = u.Evgrocoin
        elif valute1 == "Евро":
            mx = u.euro
        elif valute1 == "Доллар":
            mx = u.dollar
        elif valute1 == "Рубль":
            mx = u.rubl
        return render_template("do_sell.html", val1=valute1, val2=valute2, vol1=p1.volatil, vol2=p2.volatil, mx=mx,
                               kurs=round(p2.volatil / p1.volatil, 5))
    elif request.method == 'POST':
        kol = float(request.form["number"])
        db_sess = db_session.create_session()
        u = db_sess.query(User).filter(User.id == current_user.id).first()

        if valute1 == "NEAR":
            u.NEAR -= kol
        elif valute1 == "Bitcoin":
            u.Bitcoin -= kol
        elif valute1 == "Fynjycoin":
            u.Fynjycoin -= kol
        elif valute1 == "Saratovcoin":
            u.Saratovcoin -= kol
        elif valute1 == "Agrocoin":
            u.Evgrocoin -= kol
        elif valute1 == "Евро":
            u.euro -= kol
        elif valute1 == "Доллар":
            u.dollar -= kol
        elif valute1 == "Рубль":
            u.rubl -= kol

        p1 = db_sess.query(Valute).filter(Valute.name == valutes_names[valutes_names_human.index(valute1)]).first()
        p2 = db_sess.query(Valute).filter(Valute.name == valutes_names[valutes_names_human.index(valute2)]).first()
        kol = kol * round(p2.volatil / p1.volatil, 5)

        if valute2 == "NEAR":
            u.NEAR += kol
        elif valute2 == "Bitcoin":
            u.Bitcoin += kol
        elif valute2 == "Fynjycoin":
            u.Fynjycoin += kol
        elif valute2 == "Saratovcoin":
            u.Saratovcoin += kol
        elif valute2 == "Agrocoin":
            u.Evgrocoin += kol
        elif valute2 == "Евро":
            u.euro += kol
        elif valute2 == "Доллар":
            u.dollar += kol
        elif valute2 == "Рубль":
            u.rubl += kol

        db_sess.commit()
        return redirect('/actives')


@app.route('/choose')
def choose():
    return render_template("choose.html")


@app.route('/balance')
def balance():
    return render_template("balance.html", form=["Рубль", "Доллар", "Евро"])


@app.route('/balance/<valute1>', methods=['POST', 'GET'])
def pay(valute1):
    if request.method == 'GET':
        return render_template("pay.html", val1=valute1)
    elif request.method == 'POST':
        kol = float(request.form["number"])
        db_sess = db_session.create_session()
        u = db_sess.query(User).filter(User.id == current_user.id).first()

        if valute1 == "Евро":
            u.euro += kol
        elif valute1 == "Доллар":
            u.dollar += kol
        elif valute1 == "Рубль":
            u.rubl += kol

        db_sess.commit()
        return redirect('/actives')


@app.route('/out_balance')
def out_balance():
    return render_template("out_balance.html", form=["Рубль", "Доллар", "Евро"])


@app.route('/out_balance/<valute1>', methods=['POST', 'GET'])
def out_pay(valute1):
    if request.method == 'GET':
        db_sess = db_session.create_session()
        u = db_sess.query(User).filter(User.id == current_user.id).first()
        mx = 0
        if valute1 == "Евро":
            mx = u.euro
        elif valute1 == "Доллар":
            mx = u.dollar
        elif valute1 == "Рубль":
            mx = u.rubl
        return render_template("out_pay.html", mx=mx, val1=valute1)
    elif request.method == 'POST':
        kol = float(request.form["number"])
        db_sess = db_session.create_session()
        u = db_sess.query(User).filter(User.id == current_user.id).first()

        if valute1 == "Евро":
            u.euro -= kol
        elif valute1 == "Доллар":
            u.dollar -= kol
        elif valute1 == "Рубль":
            u.rubl -= kol

        db_sess.commit()
        return redirect('/actives')


@app.route('/addresses')
def addresses():
    return render_template("addresses.html")


if __name__ == '__main__':
    db_session.global_init("db/fynjynance.db")
    update_volatil()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)