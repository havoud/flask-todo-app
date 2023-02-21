from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy.sql import func
from datetime import datetime as dt
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hameddavoudi!'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////mnt/C:/Users/shvos/OneDrive/Desktop/My_files/HdD/21_Portfolio/06_todo_2/database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db3.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

user_todo = db.Table('user_todo',
                     db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('todo_id', db.Integer, db.ForeignKey('todo.id'))
                     )


class User(UserMixin, db.Model):
 #   __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
  #  following = db.relationship('Todo', secondary= user_todo, backref= 'followers')

    def __init__(self, username, email, password):  # , time_created):
        self.username = username
        self.email = email
        self.password = password
       # self.following = following


class Todo(db.Model):
   # __tablename__ = 'todo_1'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text())             #
    complete = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    #  time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __init__(self, title,description, complete, date_created, time_updated): #, time_created):
        self.title = title
        self.complete = complete
        self.description = description
        self.date_created = date_created
   #    self.time_created = time_created
        self.time_updated = time_updated


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')


class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return '<h1>Invalid username or password</h1>'
        # return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        #return '<h1>New user has been created!</h1>'
        return render_template('index.html', message='New user has been created!')
        #return render_template('login.html', message='New user has been created!')
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    todo_list = Todo.query.all()
    user_list = User.query.all()
    return render_template('dashboard.html', name=current_user.username, todo_list=todo_list, user_list = user_list)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/add", methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        complete = request.form['complete']
        #   date_created = dt.datetime.strptime(request.form['title'], '%Y-%m-%d').date()
        date_created = request.args.get('title')
        time_updated = request.args.get('complete')

        print(title)
        if title == "":
            return render_template('dashboard.html', message='Fill the boxes')
        if db.session.query(Todo).filter(Todo.title == title).count() == 0:
            data = Todo(title, description, complete, date_created, time_updated)
            db.session.add(data)
            db.session.commit()
            return render_template('second.html')
        return render_template('dashboard.html', message='already submitted')


@app.route("/update/<int:todo_id>")
def update(todo_id):
    todo_update = Todo.query.filter_by(id=todo_id).first()
    todo_update.complete = not todo_update.complete
    db.session.commit()
   # flash("user deleted successfully!")
    return redirect(url_for("dashboard"))


@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todo_delete = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo_delete)
    db.session.commit()
    return redirect(url_for("dashboard"))


if __name__ == '__main__':
    with app.app_context():
     db.create_all()
    app.debug = True
    app.run(debug=True)