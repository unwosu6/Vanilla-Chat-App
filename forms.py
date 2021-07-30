from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
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
    chatname = StringField('Name of Chat',
                           validators=[DataRequired(), Length(min=1, max=120)])
    display_name = StringField(
        'Display Name of Chat', validators=[
            DataRequired(), Length(
                min=1, max=120)])
    description = StringField(
        'Description', validators=[
            DataRequired(), Length(
                min=1, max=120)])
    private = BooleanField()
    submit = SubmitField('Create')


class SendMessage(FlaskForm):
    msg = StringField(
        'message', validators=[
            DataRequired(), Length(
                min=1, max=240)])
    submit = SubmitField('send')


class BecomeMember(FlaskForm):
    submit = SubmitField('Become a Member')


class Leave(FlaskForm):
    submit = SubmitField('Leave')
