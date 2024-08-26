from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask_admin import Admin
    from flask_sqlalchemy import SQLAlchemy

from Engine.admin_views.election_views import ElectionView
from flask_admin.contrib.sqla import ModelView

def setup_admin_views(main_admin: Admin, database: SQLAlchemy) -> None:

    # Adds the admin view for the Election first in relation to Candidate
    main_admin.add_view(ElectionView(name='New Election'))

    # Add an admin view for all models in the database
    from Engine.models import model_collection

    for model in model_collection:
        main_admin.add_view(ModelView(model, database.session))
