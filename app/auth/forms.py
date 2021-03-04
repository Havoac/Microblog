from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User
from flask_babel import _, lazy_gettext as _l
#validators argument in some of the fields is used to attach validation behaviors to fields

class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])             #Here I'm importing this alternative translation function and renaming to to _l() so that it looks similar to the original _(). This new function wraps the text in a special object that triggers the translation to be performed later, when the string is used.
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))

class RegistrationForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Register'))

    def validate_username(self, username):
        # if username.data != self.original_username:         #If the username entered in the form is the same as the original username, then there is no reason to check the database for duplicates.
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_('Please use a different username.'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_('Please use a different email address.'))

# class EditProfileForm(FlaskForm):
#     username = StringField('Username', validators=[DataRequired()])
#     about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
#     submit = SubmitField('Submit')

#     def __init__(self, original_username, *args, **kwargs):
#         super(EditProfileForm, self).__init__(*args, **kwargs)
#         self.original_username = original_username

#     #For the below 2 methods(validate_username() , validate_email()) : 
#     #I want to make sure that the username and email address entered by the user are not already in the database, so these two methods issue database queries expecting there will be no results. In the event a result exists, a validation error is triggered by raising ValidationError. The message included as the argument in the exception will be the message that will be displayed next to the field for the user to see
    

# class EmptyForm(FlaskForm):
#     submit = SubmitField('Submit')

# class PostForm(FlaskForm):
#     post = TextAreaField('Say something', validators=[DataRequired(), Length(min=1, max=140)])
#     submit = SubmitField('Submit')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))

class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Request Password Reset'))