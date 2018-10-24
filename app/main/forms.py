from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import User
from flask import request


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'), validators=[Length(min=0, max=240)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))


class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Submit'))


class SearchForm(FlaskForm):
    """
    Form that provides to user a tool to search text through posts of users of this Microblog app
    """
    q = StringField(_l('Seach'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):

        # Points Flask-WTF at request.args , which is where Flask writes the query string
        # arguments
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args

        # For clickable search links to work, CSRF needs to be disabled
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False

        super(SearchForm, self).__init__(*args, **kwargs)



