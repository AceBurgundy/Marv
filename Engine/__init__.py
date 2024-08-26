from Engine.admin_views.setup import setup_admin_views
from flask_admin import Admin, AdminIndexView, expose
from flask_login import LoginManager, current_user
from flask_admin.contrib.sqla import ModelView
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from Engine.config import Config
from flask_admin import Admin

login_manager: LoginManager = LoginManager()

class SecureAdminIndexView(AdminIndexView):
    """
    A custom AdminIndexView that ensures the user is authenticated
    before accessing the admin index page. If the user is not
    authenticated, they will be redirected to the login page.
    """

    @expose('/')
    def index(self):
        """
        Override the index method to check user authentication.
        Redirects unauthenticated users to the login page.
        """
        if not current_user.is_authenticated:
            return redirect(url_for('app_admin.login_form'))
        return super(SecureAdminIndexView, self).index()

class AdminModelView(ModelView):
    """
    A custom ModelView for the admin interface that restricts access
    to authenticated users only. Redirects unauthorized users to the
    login page.
    """

    def is_accessible(self):
        """
        Determines if the current user has access to the admin view.
        Returns True if the user is authenticated, meaning the user is an admin.
        """
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        """
        Redirects the user to the login page if they do not have access
        to the requested admin view.
        """
        return redirect(url_for('app_admin.login_form'))

db: SQLAlchemy = SQLAlchemy()
main_admin: Admin = Admin(index_view=SecureAdminIndexView())
socketio: SocketIO = SocketIO()

setup_admin_views(main_admin, db)

def create_app(config_class=Config) -> Flask:
    """
    Creates and configures an instance of the Flask application.

    This function initializes the Flask application, sets up the configuration,
    initializes the database and socketio, and registers the blueprints for the
    index, candidate, and error views.

    Returns:
    --------
        app: A Flask application instance.
    """
    app: Flask = Flask(__name__)
    app.config.from_object(config_class)

    login_manager.init_app(app)
    db.init_app(app)
    socketio.init_app(app)

    main_admin.init_app(app)

    from Engine.user.views import app_admin
    from Engine.index.views import index

    app.register_blueprint(index)
    app.register_blueprint(app_admin)

    def after_request(response):
        """
            Ensure responses aren't cached
        """
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

    app.after_request(after_request)

    return app
