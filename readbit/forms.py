from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired, Email, Length, NumberRange

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class SubComponentForm(FlaskForm):
    comp_name = StringField('Sub Component Name', validators=[DataRequired(), Length(max=100)],
                       render_kw={"placeholder": "Sub Comp Name"})
    weightage = IntegerField('Weightage', validators=[DataRequired(), NumberRange(min=1, max=100)],
                             render_kw={"placeholder": "Sub Comp Weight (%)"})

class MainComponentForm(FlaskForm):
    comp_name = StringField('Main Component Name', validators=[DataRequired(), Length(max=100)],
                       render_kw={"placeholder": "Main Comp Name"})
    weightage = IntegerField('Weightage', validators=[DataRequired(), NumberRange(min=1, max=100)],
                             render_kw={"placeholder": "Main Comp Weight (%)"})
    sub_comps = FieldList(FormField(SubComponentForm), label='Sub Component')
    add_sub = SubmitField(label='Add Sub Component')

class AddComponentForm(FlaskForm):
    main_comps = FieldList(FormField(MainComponentForm), label='Main Component', min_entries=1)
    add_main = SubmitField(label='Add Main Component')
    submit = SubmitField('Submit Components')