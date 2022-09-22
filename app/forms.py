from email.mime import message
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FormField, TextAreaField, FileField
from wtforms.fields.html5 import DateField
from app import app, query_db

#Nytt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Length, DataRequired, Regexp


from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from wsgiref.validate import validator
# defines all forms in the application, these will be instantiated by the template,
# and the routes.py will read the values of the fields
# TODO: Add validation, maybe use wtforms.validators??
# TODO: There was some important security feature that wtforms provides, but I don't remember what; implement it
# login_manager = LoginManager(app)
# login_manager.login_view="login"
#UserMixin,

text_validators = [
    Regexp(
        '[a-zA-Z0-9_.,!?-]$', 
        message="Only letters and numbers, no special characters."),
    Length(
        min=3,
        max=400,
        message="Your message must be in between 3 and 400 characters."),
]

profile_validators = [
    Regexp(
        '[a-zA-Z0-9]',
        message="Can only use letters and numbers."),
    Length(
        min=2,
        max=50,
        message="Your input needs to be between 2 and 50 characters"),
]

class LoginForm( FlaskForm):
    username = StringField('Username', render_kw={'placeholder': 'Username'})
    password = PasswordField('Password', render_kw={'placeholder': 'Password'})
    remember_me = BooleanField('Remember me') # TODO: It would be nice to have this feature implemented, probably by using cookies
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    first_name = StringField('First Name', render_kw={'placeholder': 'First Name'})
    last_name = StringField('Last Name', render_kw={'placeholder': 'Last Name'})
    # username = StringField('Username', validators=[InputRequired(), Length(min=3, max=15, message="At least 3 characters")], render_kw={'placeholder': 'Username'})
    username = StringField('Username', validators=[InputRequired("Username must contain at least 4 characters!"), Length(min=4, max=15, message="Username must contain at least 4 characters!")], render_kw={'placeholder': 'Username'})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=15, message="At least 4 characters")], render_kw={'placeholder': 'Password'})    
    confirm_password = PasswordField('Confirm Password', render_kw={'placeholder': 'Confirm Password'})
    submit = SubmitField('Sign Up')

class IndexForm(FlaskForm):
    login = FormField(LoginForm)
    register = FormField(RegisterForm)
#UserMixin, 
class PostForm(FlaskForm):
    content = TextAreaField('New Post', validators=[Length(max=300),Regexp('[a-zA-Z0-9]', message='Only letters and numbers')], render_kw={'placeholder': 'What are you thinking about?'})
    image = FileField('Image')
    submit = SubmitField('Post')

class CommentsForm( FlaskForm):
    comment = TextAreaField('New Comment', text_validators, render_kw={'placeholder': 'What do you have to say?'})
    submit = SubmitField('Comment')

class FriendsForm( FlaskForm):
    username = StringField('Friend\'s username', validators=[Length(min=4, max=15, message="Usernames contains between 4 and 15 characters!")], render_kw={'placeholder': 'Username'})
    submit = SubmitField('Add Friend')

class ProfileForm( FlaskForm):
    education = StringField('Education', profile_validators, render_kw={'placeholder': 'Highest education'})
    employment = StringField('Employment', profile_validators, render_kw={'placeholder': 'Current employment'})
    music = StringField('Favorite song', profile_validators, render_kw={'placeholder': 'Favorite song'})
    movie = StringField('Favorite movie', profile_validators, render_kw={'placeholder': 'Favorite movie'})
    nationality = StringField('Nationality', profile_validators, render_kw={'placeholder': 'Your nationality'})
    birthday = DateField('Birthday')
    submit = SubmitField('Update Profile')