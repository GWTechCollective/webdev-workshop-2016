import os
from flask import Flask, request, session, redirect, url_for, abort, render_template
from flask.ext.api import status
from sqlalchemy.sql.expression import func
from dank_db import *
from werkzeug import secure_filename
from werkzeug.security import check_password_hash

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
UPLOAD_FOLDER = './static/uploads'

app = Flask(__name__)
app.config.from_pyfile('dank_tank.cfg')
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/')
def show_post():
    query = request.args.get('dank_rank')

    if query == "dankest":
        post = DankPost.query.order_by(desc(DankPost.dank_rank)).limit(1).all()
    elif query == "dustiest":
        post = DankPost.query.order_by(DankPost.dank_rank).one_or_none()
    else:
        post = DankPost.query.order_by(func.random()).one_or_none()
    return render_template('show_post.html', entries=post)

@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':

        file = request.files['imgfile']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))

            new_post = DankPost(request.form['title'], filename)
            db.session.add(new_post)
            db.session.commit()

            entry = DankPost.query.order_by(DankPost.timestamp).one_or_none()
            return redirect(url_for('show_post', entries=entry))
    return render_template('upload.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).one_or_none()
        if user:

            if check_password_hash(user.passhash, request.form['password']):
                session['logged_in'] = True
                return redirect(url_for('show_post'))
            else:
                error = 'Invalid Password'
                print "Invalid Password: " + request.form['password']
        else:
            error = 'Invalid Username'
            print "Invalid Username: " + request.form['username']

    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():

    error = None

    if request.method == 'POST':
        if User.query.filter_by(username=request.form['username']).one_or_none():
            error = 'Username already taken.'
        else:
            new_user = User(request.form['username'], request.form['password'])
            db.session.add(new_user)
            db.session.commit()

    return render_template('registration.html', error=error)


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

@app.route('/categories')
def show_categories():
    return render_template('categories.html')

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run()
