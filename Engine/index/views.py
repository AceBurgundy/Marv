from flask import render_template, Blueprint

from Engine.models import Election

index: Blueprint = Blueprint('index', __name__, template_folder='templates/index', static_folder='static/index')

@index.get("/")
def _index() -> str:
    """
    Load the root page.

    Returns:
    --------
        render_template: Rendered HTML template with necessary data.
    """
    elections = Election.query.order_by(Election.created_at.desc()).all()
    return render_template("index.html", elections=elections)

