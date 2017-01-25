"""Example python server for jobs."""

from flask import Flask, request, redirect, url_for, render_template, jsonify
import flask_login

from server.util.postgres_runner import PostgresRunner
from server.util.postgres_crud import PostgresCrud
from server.auth.user import UserProvider

import os

postgresRunner = PostgresRunner("user=flask_vue dbname=flask_vue host=postgres")
usercrud = PostgresCrud(
    postgresRunner,
    "users",
    [
        {
            "name": "username",
            "extras": ["NOT NULL"]
        },
        {
            "name": "password",
            "extras": ["NOT NULL"]
        }
    ]
)

userProvider = UserProvider(usercrud)

app = Flask(__name__)
app.secret_key = 'not so secret string'  # Change this!

login_manager = flask_login.LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def user_loader(email):
    """For flask_login."""
    return userProvider.load_user(email)


@login_manager.request_loader
def request_loader(request):
    """For flask_login."""
    token = request.headers.get('Authorization')
    if token is None:
        return None
    username, password = token.split(":")  # naive token
    return userProvider.authenticate_user(username, password)


@app.after_request
def add_header(r):
    """No Cache.

    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name="World"):
    """Router for hello."""
    return "Hello " + name + "!"


@app.route("/")
def indexHTML():
    """Router for index."""
    return render_template('apps/index.html')


@app.route("/login", methods=['POST', 'GET'])
def auth():
    """Router for auth."""
    error = None
    if request.method == 'GET':
        return render_template('apps/auth.html', error=error)
    form = request.form
    if form['register'].encode('utf8').lower() == "true":
        userdata = userProvider.register_user(
            form['username'].encode('utf8'),
            form['password'].encode('utf8')
        )
    else:
        userdata = userProvider.load_authenticated_user(
            form['username'].encode('utf8'),
            form['password'].encode('utf8')
        )
    if userdata:
        user = userProvider.userdata_to_user(userdata)
        flask_login.login_user(user)
        return redirect(url_for('protected'))
    else:
        error = 'Invalid username/password'
    return render_template('apps/auth.html', error=error)


@app.route("/api/login", methods=['POST'])
def api_auth():
    """Route for ajax logins."""
    form = request.get_json(force=True)
    userdata = None
    if form['register']:
        userdata = userProvider.register_user(
            form['username'].encode('utf8'),
            form['password'].encode('utf8')
        )
    else:
        userdata = userProvider.load_authenticated_user(
            form['username'].encode('utf8'),
            form['password'].encode('utf8')
        )
    if userdata:
        user = userProvider.userdata_to_user(userdata)
        flask_login.login_user(user)
        return "true"
    raise Exception("No user loaded")


@app.route("/api/login/validate-username", methods=['POST'])
def api_auth_validate_username():
    """Public api to validate a username."""
    form = request.get_json(force=True)
    if "username" not in form:
        raise "username is required"
    return jsonify(
        userProvider.validate_username(
            form['username'].encode('utf8')
        )
    )


@login_manager.unauthorized_handler
def unauthorized():
    """Just render auth."""
    return render_template('apps/auth.html', error="unauthorized")


@app.route('/protected')
@flask_login.login_required
def protected():
    """Example protected route."""
    return 'Logged in as: ' + flask_login.current_user.id


@app.route('/logout')
def logout():
    """Log Out."""
    flask_login.logout_user()
    return 'Logged out'


@app.route('/test')
def test():
    """Allow tests to know we are operating from the same location."""
    return os.path.dirname(__file__)


"""
useful for when the app is not running via the flask command
"""
if __name__ == '__main__':
    app.run(host='0.0.0.0')
