import os
import subprocess
from dotenv.main import load_dotenv
from flask import Flask, render_template, request
from flask.helpers import url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import redirect

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://{user}:{passwd}@{host}:{port}/{table}'.format(
    user=os.getenv('POSTGRES_USER'),
    passwd=os.getenv('POSTGRES_PASSWORD'),
    host=os.getenv('POSTGRES_HOST'),
    port=5432,
    table=os.getenv('POSTGRES_DB'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class UserModel(db.Model):
    __tablename__ = 'users'

    username = db.Column(db.String(), primary_key=True)
    password = db.Column(db.String())

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return f"<User {self.username}>"

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title="Lance, Joe, Hamdia", url=os.getenv("URL"))
@app.route('/health')
def health():
    return "", 200
@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'GET':
        if request.args.get('error'):
            error = request.args['error']
        else:
            error = ""
        return render_template('register.html', title="Register", error=error)
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif UserModel.query.filter_by(username=username).first() is not None:
            error = f"User {username} is already registered."

        if error is None:
            new_user = UserModel(username, generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login', reserve_text="Successfully registered; login below"))
        else:
            return redirect(url_for('register', error=error))
@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'GET':
        if request.args.get('reserve_text'):
            reserveText = request.args['reserve_text']
        else:
            reserveText = ""
        if request.args.get('error'):
            error = request.args['error']
        else:
            error = ""
        return render_template('login.html', title="Login", error=error, reserveText = reserveText)
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        error = None
        user = UserModel.query.filter_by(username=username).first()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'

        if error is not None:
            return redirect(url_for('login', error=error))
        else:
            return redirect(url_for('blog'))

@app.route('/pull', methods=(['POST']))
def pull():
    subprocess.call("/usr/bin/sudo -s && cd /home/centos/FlaskPortfolioSite/ && /usr/bin/sudo /usr/bin/git pull && /usr/bin/sudo systemctl restart myportfolio", shell=True)
    return "", 200

@app.route('/blog', methods=(['GET']))
def blog():
    return render_template('blog.html')