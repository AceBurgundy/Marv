from wtforms.validators import DataRequired, Length, ValidationError, Email # type: ignore
from wtforms import StringField, PasswordField, EmailField # type: ignore
from flask_wtf import FlaskForm # type: ignore
from Engine.models import User
import re

def validate_username(form: FlaskForm, field: StringField) -> None:
    """
    Validate the username field.

    Args:
        form (FlaskForm): The form that contains the field.
        field (StringField): The field to be validated.

    Raises:
        ValidationError: If the username is empty or already taken.
    """
    if not field.data:
        raise ValidationError("Username cannot be empty")

    user: User = User.query.filter_by(username=field.data).first()

    if user:
        raise ValidationError("Username already taken")

def validate_email(form: FlaskForm, field: StringField) -> None:
    """
    Validate the email field.

    Args:
        form (FlaskForm): The form that contains the field.
        field (StringField): The field to be validated.

    Raises:
        ValidationError: If the email is empty or already taken.
    """
    if not field.data:
        raise ValidationError("Email cannot be empty")

    user: User = User.query.filter_by(email=field.data).first()

    if user:
        raise ValidationError("Email already taken")

def validate_password(form: FlaskForm, field: PasswordField) -> None:
    """
    Validate the password field.

    Args:
        form (FlaskForm): The form that contains the field.
        field (PasswordField): The field to be validated.

    Raises:
        ValidationError: If the password is empty, contains restricted words or characters,
                         or does not contain at least one number and one symbol.
    """
    if not field.data:
        raise ValidationError("Password cannot be empty")

    password = field.data

    restricted_words = [
        "password", "123456", "qwerty", "where", "select", "update",
        "delete", ".schema", "from", "drop"
    ]

    for word in restricted_words:
        if word.lower() in password.lower():
            raise ValidationError("Password contains a restricted word")

    for character in ["!", "#", "$"]:
        if character in password:
            raise ValidationError("Password contains a restricted character")

    if not re.search(r"\d", password):
        raise ValidationError("Password must contain at least one number")

    if not re.search(r"[!@#$%^&*()_+}{\":?></*+[;'./,]", password):
        raise ValidationError("Password must contain at least one symbol")

class RegisterForm(FlaskForm):
    """
    Form for user registration.

    Attributes:
        register_username (StringField): Field for the username input.
        register_email (StringField): Field for the email input.
        register_password (PasswordField): Field for the password input.
        register_key (PasswordField): Key required to allow the user to be added.
    """
    register_username: StringField = StringField(
        u'Username',
        id="username",
        validators=[
            DataRequired(message="Add a username"),
            Length(min=2, max=50),
            validate_username
        ]
    )

    register_email: StringField = StringField(
        u'Email',
        id="email",
        validators=[
            DataRequired(message="Should be a working email"),
            Email(),
            Length(min=2, max=120),
            validate_email,
        ]
    )

    register_password: PasswordField = PasswordField(
        u'Password',
        id="password",
        validators=[
            DataRequired("Please add a password"),
            Length(min=2, max=40),
            validate_password
        ]
    )

    register_key: StringField = StringField(
        u'Admin Key',
        id="admin_key",
        validators=[
            DataRequired(message=""),
            Length(min=4, max=20),
        ]
    )

class LoginForm(FlaskForm):
    """
    Form for user login.

    Attributes:
        login_email (EmailField): Field for the email input.
        login_password (PasswordField): Field for the password input.
    """

    login_email: EmailField = EmailField(
        u'Email',
        id="email",
        validators=[
            DataRequired(message="Should be a working email"),
            Length(min=2, max=120),
            Email(),
        ]
    )

    def validate_login_email(self, login_email: EmailField) -> None:
        """
        Validate the login email field.

        Args:
            login_email (EmailField): The email field to validate.

        Raises:
            ValidationError: If the email is empty or not found in the database.
        """
        if not login_email.data:
            raise ValidationError("Email cannot be empty")

        user = User.query.filter_by(email=login_email.data).first()

        if not user:
            raise ValidationError("\nEmail not found or User not yet registered")

    login_password: PasswordField = PasswordField(
        u'Password',
        id="password",
        validators=[
            DataRequired("Please add a password"),
            Length(min=2, max=40)
        ]
    )

    def validate_login_password(self, login_password: PasswordField) -> None:
        """
        Validate the login password field.

        Args:
            login_password (PasswordField): The password field to validate.

        Raises:
            ValidationError: If the password is empty.
        """
        if not login_password.data:
            raise ValidationError("Password cannot be empty")
