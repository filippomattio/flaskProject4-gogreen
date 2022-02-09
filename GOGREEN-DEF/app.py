import os
from datetime import date
from flask import Flask
from flask import render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Message, Mail
from flask_bcrypt import Bcrypt
# upload image
from flask_uploads import UploadSet
from flask_uploads import configure_uploads
from flask_uploads import IMAGES, patch_request_class


# use this update to fix the  from werkzeug import secure_filename, FileStorage
# ImportError: cannot import name 'secure_filename'
# pip install -U Werkzeug==0.16.0
# set maximum file size, default is 16MB


# from form import FormContact,Registration,LogForm

app = Flask(__name__)

app.config['SECRET_KEY'] = 'hard to guess'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///website_flask.db"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
# EMAIL config
app.config['MAIL_USERNAME'] = 'greengo2022@mail.com' # os.environ['username'] #qui bisogna mettere il mio indirizzo email: ex. greengo@mail.com
app.config['MAIL_PASSWORD'] = 'Greengo2022' #os.environ['password']
app.config['MAIL_TLS'] = True
app.config['MAIL_SERVER'] = 'smtp.mail.com'  # bisogna registrarsi al sito mail.com!!!
app.config['MAIL_PORT'] = 587
# Upload Configuration
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + "/static"

db = SQLAlchemy(app)
# MAIL
mail = Mail(app)
bcrypt = Bcrypt(app)

# UPLOAD Then define Upload format and file size.
photos = UploadSet('photos', IMAGES)  # max 16 MB di immagini, se di piu cambiare IMAGES e mettere la size
configure_uploads(app, photos)
patch_request_class(app)

from model import User, Role, SharingCompany
from form import RegistrationForm, LoginForm



""""@app.before_first_request
def create_db():
    db.drop_all()
    db.create_all()
    role_admin = Role(role_name='Admin')
    role_user = Role(role_name='User')
    pass_c = bcrypt.generate_password_hash("123456")  # per criptare la password
    user_admin = User( email="admin@admin.com", name="Mohammad", family_name="Ghazi", date_of_birth="1999/06/03",
                       password=pass_c,
                      role_name=role_admin)

    s1 = SharingCompany(name="Car2go", date_of_registration=date.today().strftime("%d%m%Y"),num_vehicles = 50,
                        price_per_minute = 0.26, min_age = 18, type_vehicle = "electric")
    s2 = SharingCompany(name="Enjoy", date_of_registration=date.today().strftime("%d%m%Y"), num_vehicles =40,
                        price_per_minute =0.30, min_age =18, type_vehicle ="hybrid")
    s3 = SharingCompany(name="Dot", date_of_registration=date.today().strftime("%d%m%Y"), num_vehicles =50,
                        price_per_minute =0.11, min_age = 16, type_vehicle ="electric")

    db.session.add_all([role_admin, role_user])
    db.session.add(user_admin)
    db.session.add(s1)
    db.session.add(s2)
    db.session.add(s3)
    db.session.commit()
    # user_query = User.query.filter_by(username="admin").first()
    # print(user_query.name)

"""

@app.route('/')
def homepage():  # put application's code here
    username = session.get('username')
    return render_template("home.html", username=username)


def send_mail(to, subject, template, **kwargs):  # to is could be a list
    msg = Message(subject, recipients=[to], sender=app.config['MAIL_USERNAME'])
    # msg.body= render_template(template + '.txt',**kwargs) solo uno dei due puo essere usato, non entrambi!
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)


@app.route('/login3', methods=['POST', 'GET'])
def login_page():
    if 'email' in session:
        return redirect(url_for('confront_price'))
    form = LoginForm()
    #if form.validate_on_submit():
    email = form.email.data
    password = form.password.data
    user = User.query.filter_by(email=form.email.data).first()
    if user:
        session['email'] = email
        if bcrypt.check_password_hash(user.password, password):
            return redirect(url_for('confront_price'))
    return render_template('login3.html', form=form, email=email, password=password)


@app.route('/logout', methods=['POST', 'GET'])
def logout_page():
    session.clear()
    return redirect(url_for('homepage'))


@app.route('/registration', methods=['POST', 'GET'])
def register_page():
    form = RegistrationForm()
    if form.validate_on_submit():
        role_name = Role.query.filter_by(role_name="User").first()
        pass_c = bcrypt.generate_password_hash(form.password.data)
        new_user = User(email=form.email.data,
                        name=form.name.data,
                        family_name=form.family_name.data,
                        date_of_birth=form.date_of_birth.data,
                        password=pass_c,
                        role_name=role_name)
        #form.validate_email(form)
        db.session.add(new_user)
        db.session.commit()
       # send_mail(form.email.data, "New registration", "mail", name=form.name.data, password=form.password.data,
        #          email=form.email.data)
        session['email'] = form.email.data
        return redirect(url_for('confront_price'))
    return render_template('registration.html', form=form)

@app.route('/reserve', methods=['POST', 'GET'])
def confront_price():
    ord = SharingCompany.query.order_by(SharingCompany.price_per_minute)
    return render_template('reserve.html', ord=ord)

#@app.route('/login3', methods=['POST', 'GET'])
#def login3():
 #   return render_template('login3.html')

@app.route('/login2', methods=['POST', 'GET'])
def login2():
    return render_template('login2.html')

@app.route('/registration2', methods=['POST', 'GET'])
def reg2():
    return render_template('registration2.html')

@app.route('/settings', methods=['POST', 'GET'])
def set():
    return render_template('settings.html')

if __name__ == '__main__':
    app.run(debug=True)
