import os, json
from datetime import datetime
from flask import Flask, request, session, redirect, url_for, abort, render_template
from flask.ext.api import status
from sqlalchemy.sql.expression import func
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, Integer, String, Column, DateTime
from werkzeug import secure_filename

#config
DATABASE = 'tmp/dank.db'
DEBUG = True
SECRET_KEY = 'secret'
USERNAME = 'admin'
PASSWORD = 'password'
UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

print 'Set Config'

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE
db = SQLAlchemy(app)


class DankPost(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(128), unique=False)
    filename = Column(String(128), unique=False)
    dank_rank = Column(Integer, unique=False)
    timestamp = Column(DateTime, unique=False)

    def __init__(self, title, filename):
        self.title = title
        self.filename = filename
        self.dank_rank = 0
        self.timestamp = datetime.utcnow()

db.create_all()

@app.route('/')
def show_post():
    query = request.args.get('dank_rank')

    if query == "dankest":
        post = DankPost.query.order_by(desc(DankPost.dank_rank)).limit(1).all()
    elif query == "dustiest":
        post = DankPost.query.order_by(DankPost.dank_rank).limit(1).all()
    else:
        post = DankPost.query.order_by(func.random()).limit(1).all()
    return render_template('show_post.html', entries=post)

@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)

    if request.method == 'POST':

        file = request.files['imgfile']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))

            new_post = DankPost(request.form['title'], filename)
            db.session.add(new_post)
            db.session.commit()

            entry = DankPost.query.filter_by(title=new_post.title, filename=new_post.filename).all()
            return redirect(url_for('show_post'))
    return render_template('upload.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid Username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid Password'
        else:
            session['logged_in'] = True
            return redirect(url_for('show_post'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('show_post'))

@app.route('/vote', methods=['GET', 'POST'])
def vote():

    post = DankPost.query.get(request.form['id'])

    if request.form['vote'] == "up":
        post.dank_rank += 1
    elif request.form['vote'] == "down":
        post.dank_rank -= 1
    else:
        pass

    db.session.commit()
    return ('', status.HTTP_200_OK)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run()
