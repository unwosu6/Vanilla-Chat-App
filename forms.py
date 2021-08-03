from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, \
    BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, \
    InputRequired, ValidationError
from flask import Flask


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=25)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Confirm Password', validators=[
            DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])

    remember = BooleanField()

    submit = SubmitField('Login')


class NewChat(FlaskForm):
    # must make it so that chatname is unique
    chatname = StringField('[chat code]',
                           validators=[DataRequired(), Length(min=1, max=120)])
    display_name = StringField(
        '[display name of chat]', validators=[
            DataRequired(), Length(
                min=1, max=120)])
    description = TextAreaField(
        '[description]', validators=[
            DataRequired(), Length(
                min=1, max=120)])
    private = BooleanField()
    submit = SubmitField('create chat')


class InviteToChat(FlaskForm):
    chatname = SelectField('[select chat]', coerce=int)
    submit = SubmitField('invite')


class SendMessage(FlaskForm):
    msg = StringField(
        'message', validators=[
            Length(
                min=0, max=240)])
    submit2 = SubmitField('send')


class BecomeMember(FlaskForm):
    submit = SubmitField('Become a Member')


class Leave(FlaskForm):
    submit = SubmitField('Leave')


class EditChat(FlaskForm):
    display_name = StringField(
        '[display name of chat]', validators=[
            DataRequired(), Length(
                min=1, max=120)])
    description = TextAreaField(
        '[description]', validators=[
            DataRequired(), Length(
                min=1, max=120)])
    owner = SelectField('[select new owner]', coerce=int)
    user = SelectField('[select user to remove]', coerce=int)
    submit = SubmitField('save changes')
