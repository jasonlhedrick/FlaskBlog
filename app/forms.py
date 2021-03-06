from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, BooleanField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User

#############################################
#### WTForm for Creating/Updating a Post ####
#############################################
class PostForm(FlaskForm):
    post_title = StringField("Post Title",
                validators=[DataRequired()])
    post_body = TextAreaField("Post Body",
                validators=[DataRequired()])
    submit = SubmitField("Post")

######################################
#### WTForm for Logging a User in ####
######################################
class LoginForm(FlaskForm):
    email = StringField("Email", 
                validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField("Login")

##################################################
#### WTForm for Registering a User Account in ####
##################################################
class RegistrationForm(FlaskForm):
    username = StringField("Username", 
                validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField("Email", 
                validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", 
                validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Sign up")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()

        if user:
            raise ValidationError('Username already in use.')
    
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()

        if email:
            raise ValidationError('Email already in use.')

############################################
#### WTForm for Updating a User Account ####
############################################
class UpdateAccountForm(FlaskForm):
    username = StringField("Username", 
                            validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField("Email", 
                        validators=[DataRequired(), Email()])
    profile_picture = FileField('Update Profile Picture', 
                                validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField("Update Account")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already in use.')
    
    def validate_email(self, email):
        if email.data != current_user.email:
            email = User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError('Email already in use.')

class RequestPasswordResetForm(FlaskForm):
    email = StringField("Email", 
                        validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()

        if email is None:
            raise ValidationError('There is no account associated with that email.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", 
                validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Reset Password")