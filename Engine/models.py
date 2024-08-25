from typing import List, Type
from sqlalchemy import Column, Integer, DateTime as SQLAlchemyDateTime, ForeignKey, Text, String
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from Engine import login_manager, db
from flask_login import UserMixin # type: ignore

@login_manager.user_loader
def load_user(user_id: str):
    """
    Loads the current user
    """
    return User.query.get(int(user_id))

class BaseModel(db.Model):  # type: ignore
    """
    Base model with common attributes for all models.

    Attributes:
        id: The unique identifier for the record.
        created_at: The timestamp when the record was created.
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(SQLAlchemyDateTime, default=datetime.now(timezone.utc))

    @staticmethod
    def datetime_readable(datetime: datetime) -> str:
        """
        Convert a datetime object into a more readable string format.

        Args:
            datetime (DateTime): The datetime object to format.

        Returns:
            str: The formatted datetime string.
        """
        return datetime.strftime('%B %Y %I:%M%p')

class User(BaseModel, UserMixin):
    """
    Represents an administrator with access to manage various aspects of the application.

    Attributes:
        username: The username of the admin.
        email: The email address of the admin.
        password_hash: The hashed password of the admin.
    """
    __tablename__ = 'users'

    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    def __init__(self, username, email, password_hash) -> None:
        """
        Initialize an User instance.

        Args:
            username (str): The username of the admin.
            email (str): The email address of the admin.
            password_hash (str): The hashed password of the admin.
        """
        self.username = username
        self.email = email
        self.password_hash = password_hash

    def __repr__(self) -> str:
        return f'<User {self.username}>'

class Candidate(BaseModel):
    """
    Represents a candidate for a position in an election.

    Attributes:
        name: The name of the candidate.
        image_filename: The URL of the candidate's image.
        id_number: An optional identifier for the candidate.
        position_id: The foreign key referencing the Position.
        election_id: The foreign key referencing the Election.
    """
    __tablename__ = 'candidates'

    name = Column(String(255), nullable=False)
    image_filename = Column(Text, nullable=True)
    id_number = Column(String(255), unique=True, nullable=True)

    position_id = Column(Integer, ForeignKey('positions.id'), nullable=False)
    election_id = Column(Integer, ForeignKey('elections.id'), nullable=False)

    position = relationship('Position')
    election = relationship('Election')

    def votes(self) -> int:
        """
        Returns the number of votes the candidate have.

        To show the votes a candidate have for a specific election, query the election first

        election = Election.query.get(id)

        >>> for candidate in election.candidates:
        >>>     candidate.votes() # will return the vote count for that candidate on this election
        """
        return Vote.query.filter_by(election_id=self.election_id, candidate_id=self.id).count()

class Course(BaseModel):
    """
    Represents a course.

    Attributes:
        name: The name of the course
    """
    __tablename__ = 'courses'

    name = Column(String(255), unique=True, nullable=False)

class Election(BaseModel):
    """
    Represents an election with voting sections.

    Attributes:
        title: The title of the election (e.g., "2024 School Presidential Elections").
        start_time: The datetime when voting starts.
        end_time: The datetime when voting ends.
        positions: A relationship to the Position model.
    """
    __tablename__ = 'elections'

    title = Column(String(255), nullable=False, unique=True)
    start_time = Column(SQLAlchemyDateTime, nullable=False)
    end_time = Column(SQLAlchemyDateTime, nullable=False)

    candidates = relationship('Candidate', foreign_keys='Candidate.election_id', order_by='desc(Candidate.created_at)')

class Organization(BaseModel):
    """
    Represents an organization where a student belongs.

    Attributes:
        name: The name of the organization (e.g., "College of Engineering and Technology").
    """
    __tablename__ = 'organizations'

    name = Column(String(255), nullable=False)

class Position(BaseModel):
    """
    Represents a position within an election (e.g., "President").

    Attributes:
        name: The name of the position.
    """
    __tablename__ = 'positions'

    name = Column(String(255), nullable=False, unique=True)

class Voter(BaseModel):
    """
    Represents a voter in the election system.

    Attributes:
        first_name: The first name of the voter.
        middle_name: The optional middle name of the voter.
        last_name: The last name of the voter.
        suffix: The optional suffix for the voter (e.g., "Jr.", "Sr.").
        id_number: An optional identifier for the voter.
        course_id: The optional foreign key referencing the Course.
        course: A relationship to retrieve the parent Course.
        organization_id: The optional foreign key referencing the Organization.
        organization: A relationship to retrieve the parent Organization.
    """
    __tablename__ = 'voters'

    first_name = Column(String(255), nullable=False)
    middle_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=False)
    suffix = Column(String(255), nullable=True)
    id_number = Column(String(255), unique=True, nullable=True)

    course_id = Column(Integer, ForeignKey('courses.id'), nullable=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True)

    course = relationship('Course')
    organization = relationship('Organization')

    def get_name(self) -> str:
        """
        Returns the full name of the voter in the format "First Middle Last Suffix".

        Returns:
            str: The full name of the voter.
        """
        middle_name: str = str(self.middle_name if self.middle_name else '')
        suffix: str = str(self.suffix if self.suffix else '')

        return f"{self.first_name} {middle_name} {self.last_name} {suffix}"

class Vote(BaseModel):
    """
    Association table for many-to-many relationship between Voter and Candidate.

    Attributes:
        voter_id: The foreign key referencing the Voter.
        candidate_id: The foreign key referencing the Candidate.
        election_id: The foreign key referencing the Election.
    """
    __tablename__ = 'Votes'

    voter_id = Column(Integer, ForeignKey('voters.id'))
    candidate_id = Column(Integer, ForeignKey('candidates.id'))
    election_id = Column(Integer, ForeignKey('elections.id'))

model_collection: List[Type[BaseModel]] = [
    User,
    Candidate,
    Course,
    Election,
    Organization,
    Position,
    Voter,
    Vote
]