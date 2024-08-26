from wtforms import StringField, SelectField, FieldList, FormField, DateTimeField
from werkzeug.wrappers.response import Response
from flask import request, redirect, url_for
from wtforms.validators import DataRequired
from flask_admin import BaseView, expose
from flask_wtf import FlaskForm
from typing import Dict, List, Union

class DataListField(StringField):
    def __init__(self, label=None, validators=None, datalist=None, **kwargs):
        super(DataListField, self).__init__(label, validators, **kwargs)
        self.datalist = datalist or []

    def __call__(self, **kwargs):
        kwargs['list'] = f'datalist_{self.name}'
        html = super(DataListField, self).__call__(**kwargs)
        datalist_html = '\n'.join([
            f'<datalist id="datalist_{self.name}">',
                '\n'.join([f'<option value="{item}">' for item in self.datalist]),
            '</datalist>'
        ])

        return f"{html}{datalist_html}"

class CandidateForm(FlaskForm):
    """
    Form for creating or updating a candidate.

    Attributes:
        name: The candidate's name.
        image_filename: The filename of the candidate's image.
        id_number: The candidate's ID number.
        position: The position the candidate is running for.
    """
    name: StringField = StringField('Name', default="Juan Dela Cruz", validators=[DataRequired()])
    image_filename: StringField = StringField('Image', default="sdgadghh", validators=[DataRequired()])
    id_number: StringField = StringField('ID Number', default="sdgadghh", validators=[DataRequired()])
    position: DataListField = DataListField('Position')

    def __init__(self, *args, **kwargs) -> None:
        """
        Initializes the CandidateForm with position choices from the database.

        Args:
            *args: Variable length argument list.
            **kwargs: Keyword arguments.
        """
        super(CandidateForm, self).__init__(*args, **kwargs)
        from Engine.models import Position
        self.position.datalist = [position.name for position in Position.query.all()]

class ElectionForm(FlaskForm):
    """
    Form for creating or updating an election.

    Attributes:
        title: The title of the election.
        start_date_and_time: The start date and time of the election.
        end_date_and_time: The end date and time of the election.
        candidates: A list of candidate forms.
    """
    title: StringField = StringField('Election Title', default="sdgadghh", validators=[DataRequired()])
    start_date_and_time: DateTimeField = DateTimeField('Start Date and Time', format='%Y-%m-%dT%H:%M', validators=[])
    end_date_and_time: DateTimeField = DateTimeField('End Date and Time', format='%Y-%m-%dT%H:%M', validators=[])
    candidates: FieldList = FieldList(FormField(CandidateForm), min_entries=1)

class ElectionView(BaseView):
    """
    View for managing elections in the admin interface.

    Methods:
        index: Displays the form for creating or updating an election and handles form submission.
    """
    @expose('/', methods=('GET', 'POST'))
    def index(self) -> Union[Response, str]:
        """
        Handles GET and POST requests for creating or updating an election.

        Returns:
            Response or str: The rendered template or redirect response.
        """
        from Engine.models import Election, Candidate, Position
        from Engine import db

        form: ElectionForm = ElectionForm(request.form)

        if request.method == 'GET':
            return self.render('admin/new_election.html', form=form)

        if not form.validate_on_submit():
            # Print out validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error in {field}: {error}")

            return self.render('admin/new_election.html', form=form)

        election: Election = Election(
            form.title.data,
            form.start_date_and_time.data,
            form.end_date_and_time.data
        )

        db.session.add(election)
        db.session.commit()

        # Collect all unique positions from candidate data
        positions_data: set = set(candidate_data['position'] for candidate_data in form.candidates.data)

        # Query all existing positions in bulk
        position_filter = Position.name.in_(positions_data)
        existing_positions: List = Position.query.filter(position_filter).all()

        existing_positions_map: Dict[str, int] = {
            position.name: position.id for position in existing_positions
        }

        # Determine new positions to add
        new_positions: List[Position] = []

        for position_name in positions_data:
            if position_name not in existing_positions_map.keys():
                new_positions.append(Position(name=position_name))

        # Bulk insert new positions
        if new_positions:
            db.session.add_all(new_positions)
            db.session.commit()

        # Update the positions map
        for position in new_positions:
            existing_positions_map[str(position.name)] = int(position.id)

        # Collect candidates
        candidates: List[Candidate] = []

        for candidate_data in form.candidates.data:
            position_id: int = existing_positions_map[candidate_data['position']]
            candidates.append(
                Candidate(
                    name=candidate_data['name'],
                    image_filename=candidate_data['image_filename'],
                    id_number=candidate_data['id_number'],
                    position_id=position_id,
                    election_id=election.id
                )
            )

        # Bulk insert candidates
        db.session.add_all(candidates)
        db.session.commit()

        return redirect(url_for('.index'))
