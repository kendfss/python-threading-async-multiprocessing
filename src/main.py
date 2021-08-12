import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
render_template, flash

app = Flask(__name__)
app.config.from_object(__name__)

__app_name__ = "gnatr"
# __db_name__ = f"{__app_name__}.db"
__db_name__ = f"{__app_name__}-users.db"
__db_path__ = os.path.join(app.root_path, __db_name__)
__user_db__ = os.path.join(app.root_path, __db_name__)
databases = {
    "": {
        f""
    }
}

app.config.update(dict(
    DATABASE=__db_path__,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD=''
))


# app.config.from_envvar(f'{__app_name__}_SETTINGS', silent=True)

####################################################################################
#                                     DATABASE                                     # 
####################################################################################

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv
def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def init_db():
    if os.path.exists(__db_path__):
        return 1
    with app.open_resource('schema.sql', mode='r') as f, get_db() as db:
        db.cursor().executescript(f.read())
        db.commit()
@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    match init_db():
        case None:
            print('Initialized the database')
        case 1:
            print('Database already exists!')


def rm_db():
    if not os.path.exists(__db_path__):
        return 1
    os.remove(__db_path__)
@app.cli.command('rmdb')
def rmdb_command():
    """Removes the database."""
    match rm_db():
        case None:
            print('Removed the database')
        case 1:
            print('Database doesn\'t exist!')

################################################################
#                            ROUTES                            # 
################################################################

@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute(
        'insert into entries (title, text) values (?, ?)',
        [request.form['title'], request.form['text']]
    )
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    # errors = {}
    if request.method == 'POST':
        un = request.form['username'] != app.config['USERNAME']
        pw = request.form['password'] != app.config['PASSWORD']
        
        if un and pw:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
        else:
            error = ''
            error += ('Invalid username', '')[un]
            error += ('Invalid password', '')[pw]

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))