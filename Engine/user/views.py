from flask import Blueprint, Response, jsonify, redirect, render_template, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.wrappers.response import Response as RedirectResponse
from Engine.user.forms import RegisterForm, LoginForm
from flask_login import login_user, logout_user
from Engine.models import User
from typing import Optional
from Engine import db
import traceback

app_admin: Blueprint = Blueprint('app_admin', __name__, template_folder='templates/user', static_folder='static/user')

@app_admin.get("/admin/login")
def login_form() -> str:
    """
    Displays login form.

    Returns:
        rendered login.html template with the login form
    """
    logout_user()
    form: LoginForm = LoginForm()
    return render_template("login.html", form=form)

@app_admin.post("/admin/login")
def login() -> Response:
    """
    Logs user in.

    Returns:
        - JSON response with status=success if login is successful
        - JSON response with status=error, error message, and form errors if login is unsuccessful
    """
    form: LoginForm = LoginForm(request.form)
    email_input: str = form.login_email.data.strip()

    if not form.validate():
        return jsonify({
            'status': 'error',
            'message': [field.errors for field in form if field.errors]
        })

    user: Optional[User] = User.query.filter_by(email=email_input).first()

    if user and check_password_hash(str(user.password_hash), form.login_password.data):
        login_user(user)
        return jsonify({
            'status': 'success',
            'url': url_for('admin.index')
        })

    return jsonify({
        'status': 'error',
        'message': ["No matching password"]
    })

@app_admin.get("/admin/logout")
def logout() -> RedirectResponse:
    """
    Logs user out.

    Returns:
        Redirects to the login_form route
    """
    logout_user()
    return redirect(url_for('app_admin.login_form'))

@app_admin.get("/admin/register")
def register_form() -> str:
    """
    Displays registration form.

    Returns:
        rendered register.html template with the registration form
    """
    return render_template("register.html", form=RegisterForm())

@app_admin.post("/admin/register")
def register() -> RedirectResponse:
    """
    Registers user.

    Returns:
        - Redirects to the login_form route if registration is successful
        - Renders the register.html template with form errors if registration is unsuccessful
    """
    form: RegisterForm = RegisterForm(request.form)

    if not form.validate():
        return jsonify({
            'status': 'error',
            'message': [field.errors for field in form if field.errors]
        })

    try:
        if form.register_key.data != 'AS34FH3':
            return jsonify({
                'status': 'error',
                'message': ["Not the key I'm looking for", "Ask any of the admin for the key"]
            })

        user: User = User(
            username=form.register_username.data,
            email=form.register_email.data,
            password_hash=generate_password_hash(form.register_password.data)
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'url': url_for('app_admin.login_form')
        })

    except Exception as error:
        print(f"{error}")
        traceback.print_exc()

        return jsonify({
            'status': 'error',
            'message': ["Error in registering user"]
        })