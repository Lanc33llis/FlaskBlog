import os
from flask import Flask, render_template, send_from_directory, Response, request
from dotenv import load_dotenv
from flask.helpers import url_for
from flask.typing import StatusCode
from werkzeug.sansio.response import Response
from werkzeug.utils import redirect
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db
import subprocess

load_dotenv()
app = Flask(__name__)
app.config['DATABASE'] = os.path.join(os.getcwd(), 'flask.sqlite')
db.init_app(app)

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
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = f"User {username} is already registered."

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
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
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
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